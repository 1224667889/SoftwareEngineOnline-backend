"""作业管理"""
from models.users import User
from . import admin
from flask import request
from servers import homeworks
from utils.middleware import login_required
from utils.split import send_shell
from utils import serialization
import datetime


# 上传文件
@admin.route("/homework/document", methods=['POST'])
@login_required("SuperAdmin", "Admin")
def document_upload(login_user: User):
    file = request.files['file']
    d, e = homeworks.upload_document(file)
    if e:
        return serialization.make_resp({"error_msg": "文档上传失败"}, code=500)
    return serialization.make_resp({"detail": d.get_msg()}, code=200)


# 发布作业
@admin.route("/homework", methods=['POST'])
@login_required("SuperAdmin", "Admin")
def new_homework(login_user: User):
    try:
        title = request.json.get("title")
        if not title:
            return serialization.make_resp({"error_msg": "未填写标题"}, code=400)
        url = request.json.get("url")
        if not url:
            return serialization.make_resp({"error_msg": "未填写博客链接"}, code=400)
        team_type = int(request.json.get("team_type"))     # 0:单人;1:结对;2:团队
        if team_type > 2 or team_type < 0:
            return serialization.make_resp({"error_msg": "作业类型错误"}, code=400)
        weight = int(request.json.get("weight"))
        scores = list(request.json.get("scores"))
    except Exception as e:
        return serialization.make_resp({"error_msg": "参数格式错误"}, code=400)
    try:
        begin_at = datetime.datetime.fromtimestamp(int(request.json.get("begin_at")))   # 开始时间
        deadline = datetime.datetime.fromtimestamp(int(request.json.get("deadline")))   # 结束时间
        over_at = datetime.datetime.fromtimestamp(int(request.json.get("over_at")))     # 公示时间
    except Exception as e:
        return serialization.make_resp({"error_msg": "时间类型错误"}, code=400)
    document_u_name_list = request.json.get("documents").split(",")
    splits = request.json.get("splits").split(",")
    documents = [homeworks.find_document_u_name(u_name) for u_name in document_u_name_list]
    task, err = homeworks.create_homework(
        url,
        title,
        team_type,
        begin_at,
        deadline,
        over_at,
        weight,
        documents,
        splits,
        scores,
        login_user
    )
    if err:
        return serialization.make_resp({"error_msg": "上传错误:" + str(err)}, code=500)
    err = send_shell(
        task.id,
        task.url,
        datetime.datetime.timestamp(task.begin_at),
        datetime.datetime.timestamp(task.deadline)
    )
    if err:
        return serialization.make_resp({"error_msg": "爬虫启动失败:" + str(err)}, code=500)
    return serialization.make_resp({"task": task.get_msg()}, code=200)


# 查询作业详情(可查询已删除) - 管理员
@admin.route("/homework/<string:task_id>", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_detail_admin(login_user: User, task_id):
    task = homeworks.find_by_id_force(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    return serialization.make_resp({"task": task.get_msg()}, code=200)


# 查询作业列表(可含删除)
@admin.route("/homework/index", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_index_admin(login_user: User):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    team_type = request.args.get("team_type", -1, type=int)
    keyword = request.args.get('keyword', "")
    is_delete = request.args.get('is_delete', -1, type=int)
    tasks, total_page, num = homeworks.find_by_team_type_page(
        team_type,
        page_number,
        page_size,
        keyword,
        is_delete
    )
    return serialization.make_resp(
        {
            "tasks": [task.get_index() for task in tasks],
            "total_page": total_page,
            "num": num
        },
        code=200
    )


# 删除/恢复作业
@admin.route("/homework/<string:task_id>", methods=['PUT'])
@login_required("SuperAdmin", "Admin")
def homework_change(login_user: User, task_id):
    task = homeworks.find_by_id_force(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    err = task.change_state()
    if err:
        return serialization.make_resp({"error_msg": "修改失败"}, code=500)
    return serialization.make_resp({"task": task.get_msg()}, code=200)


# 设置权重
@admin.route("/homework/<string:task_id>/weight", methods=['PUT'])
@login_required("SuperAdmin", "Admin")
def homework_change_weight(login_user: User, task_id):
    task = homeworks.find_by_id_force(task_id)
    weight = request.form.get("weight", default=0, type=int)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    err = task.change_weight(weight)
    if err:
        return serialization.make_resp({"error_msg": "修改失败"}, code=500)
    return serialization.make_resp({"task": task.get_msg()}, code=200)


# 查询所有排名 - 管理员不需要等待公示
@admin.route("/homework/<string:task_id>/rank", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_rank_admin(login_user: User, task_id):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    ranks = []
    docs, page, num = task.get_all_rank(page_number, page_size)
    for doc in docs:
        ranks.append({
            "id": doc["id"],
            "max": doc["max"],
            "sum": doc["sum"],
            "scores": list(doc["scores"].values()),
            "delay": doc["task"]["delay"]
        })
    return serialization.make_resp({
        "num": num,
        "total_page": page,
        "ranks": ranks,
    }, code=200)


# 查询所有分块得分 - 管理员不需要等待公示
@admin.route("/homework/<string:task_id>/<string:split_id>/scores", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_split_rank_admin(login_user: User, task_id, split_id):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    if split_id == "0":
        sp = task.splits.first()
    else:
        sp = task.splits.filter_by(id=split_id).first()
    if not sp:
        return serialization.make_resp({"error_msg": "分块不存在"}, code=404)
    ranks = []
    docs, page, num = sp.get_mongo_some_doc_finished(page_number, page_size)
    for doc in docs:
        ranks.append({
            "score": doc["scores"][f"{sp.id}"],
            "id": doc["id"]
        })
    return serialization.make_resp({
        "num": num,
        "page": page,
        "ranks": ranks,
    }, code=200)


# 查询作业得分
@admin.route("/homework/<string:task_id>/result", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_score_student(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    if task.get_status() < 3:
        return serialization.make_resp({"error_msg": "结果未开放"}, code=401)
    doc_id = request.args.get("id", 0, type=int)
    doc, scores, delay = task.get_doc_scores(doc_id)
    if not scores:
        return serialization.make_resp({"error_msg": "未找到作业记录"}, code=404)
    return serialization.make_resp({
        "scores": list(scores.values()),
        "delay": int(delay),
        "max": doc["max"],
        "sum": doc["sum"],
    }, code=200)


