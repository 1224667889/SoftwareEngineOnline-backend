"""作业功能"""
from . import user
from flask import request, Response
from models.users import User
from servers import homeworks
from utils.middleware import login_required
from utils import serialization
from utils.logger import logger
from config import documents_path


# 下载文档
@user.route("/homework/document/<string:u_name>", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def document_upload(login_user: User, u_name):
    document = homeworks.find_document_u_name(u_name)
    if not document:
        return serialization.make_resp({"error_msg": "文档不存在"}, code=404)
    try:
        # 流式文件
        def send_file():
            store_path = documents_path + document.u_name
            with open(store_path, 'rb') as f:
                while 1:
                    data = f.read(1 * 1024 * 1024)  # 每次读取1MB (可用限速)
                    if not data:
                        break
                    yield data
        response = Response(send_file(), content_type='application/octet-stream')
        response.headers["Content-disposition"] = 'attachment; filename=%s' % \
                                                  document.name.encode("utf-8").decode("latin1")
        return response
    except Exception as e:
        logger.error(e)
        return serialization.make_resp({"error_msg": "文档返回失败"}, code=500)


# 查询作业列表
@user.route("/homework/index", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_index(login_user: User):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    team_type = request.args.get("team_type", -1, type=int)
    keyword = request.args.get('keyword', "")
    tasks, total_page, num = homeworks.find_by_team_type_page(team_type, page_number, page_size, keyword, False)
    return serialization.make_resp(
        {
            "tasks": [task.get_index() for task in tasks],
            "total_page": total_page,
            "num": num
        },
        code=200
    )


# 查询作业详情 - 学生
@user.route("/homework/<string:task_id>", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_detail(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    return serialization.make_resp({"task": task.get_msg_safe()}, code=200)


# 查询作业得分
@user.route("/homework/<string:task_id>/result", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_score_student(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    if task.get_status() < 3:
        return serialization.make_resp({"error_msg": "结果未开放"}, code=401)
    task_team = task.get_task_team_by_user(login_user)
    if not task_team:
        return serialization.make_resp({"error_msg": "查询不到队伍信息"}, code=404)
    doc, scores, delay = task.get_doc_scores(task_team.id)
    if not scores:
        return serialization.make_resp({"error_msg": "未找到作业记录"}, code=404)
    return serialization.make_resp({
        "scores": list(scores.values()),
        "delay": int(delay),
        "max": doc["max"],
        "sum": doc["sum"],
    }, code=200)


# 查询排名
@user.route("/homework/<string:task_id>/rank", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_rank_student(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    if task.get_status() < 3:
        return serialization.make_resp({"error_msg": "结果未开放"}, code=401)
    task_team = task.get_task_team_by_user(login_user)
    if not task_team:
        return serialization.make_resp({"error_msg": "查询不到队伍信息"}, code=404)
    doc, scores, delay, rank_num, total_num = task.get_doc_rank(task_team.id)
    if not doc:
        return serialization.make_resp({"error_msg": "未找到作业记录"}, code=404)
    return serialization.make_resp({
        "title": task.title,
        "scores": list(scores.values()),
        "rank_num": rank_num + 1,
        "total_num": total_num,
        "delay": int(delay),
        "sum": doc["sum"],
        "max": doc["max"]
    }, code=200)


# 查询作业提交情况
@user.route("/homework/<string:task_id>/upload", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def check_homework_student(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    task_team = task.get_task_team_by_user(login_user)
    if not task_team:
        return serialization.make_resp({"error_msg": "查询不到队伍信息"}, code=404)
    doc = task.get_mongo_group().find_one({"id": task_team.id})
    if not doc:
        return serialization.make_resp({"error_msg": "未找到作业记录"}, code=404)
    return serialization.make_resp({
        "url": doc["task"]["url"],
    }, code=200)


# 查询所有分块得分 - 普通用户需要等待公示
@user.route("/homework/<string:task_id>/<string:split_id>/scores", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def homework_split_rank(login_user: User, task_id, split_id):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    if task.get_status() < 3:
        return serialization.make_resp({"error_msg": "结果未开放"}, code=401)
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
