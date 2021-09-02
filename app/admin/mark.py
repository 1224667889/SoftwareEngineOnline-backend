"""作业批改"""
from models.users import User
from . import admin
from servers import homeworks, users
from utils.middleware import login_required, spider_jwt
from utils import serialization
from flask import request, make_response
import time
from utils.split import parse_blog
import xlsxwriter
from io import BytesIO
import datetime


# 返回分割点
@admin.route("/homework/<string:task_id>/splits", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_splits(login_user: User, task_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    return serialization.make_resp({"splits": task.get_splits()}, code=200)


# 获取一个未批改的作业
@admin.route("/homework/<string:task_id>/<string:split_id>", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_split_detail(login_user: User, task_id, split_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    sp = task.splits.filter_by(id=split_id).first()
    if not sp:
        return serialization.make_resp({"error_msg": "分块不存在"}, code=404)
    doc = sp.get_mongo_doc()
    if not doc:
        return serialization.make_resp({"error_msg": "该作业不存在"}, code=404)
    html = doc["task"]["html"]
    return serialization.make_resp({"split": sp.get_msg(), "html": parse_blog([sp.title], html).get(sp.title, "")}, code=200)


# 提交批改
@admin.route("/homework/<string:task_id>/<string:split_id>", methods=['PUT'])
@login_required("SuperAdmin", "Admin")
def homework_mark(login_user: User, task_id, split_id):
    task = homeworks.find_by_id(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    sp = task.splits.filter_by(id=split_id).first()
    if not sp:
        return serialization.make_resp({"error_msg": "分块不存在"}, code=404)
    try:
        scores_json = request.json
        doc_id = scores_json["id"]
        doc = sp.get_mongo_doc_by_id(doc_id)
        if not doc:
            return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
        scores_list = list(scores_json.get("scores"))
    except Exception as e:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    try:
        for score in scores_list:
            s = sp.scores.filter_by(id=score["id"]).first()
            if not s:
                return serialization.make_resp({"error_msg": "评分点不存在"}, code=404)
            if s.max < score["score"] or score["score"] < 0:
                return serialization.make_resp({"error_msg": "分数不在范围内"}, code=400)
            doc["scores"][f'{score["id"]}']["score"] = score["score"]
            doc["scores"][f'{score["id"]}']["referee"] = login_user.name
            doc["scores"][f'{score["id"]}']["mark_at"] = int(time.time())
            sum_score = 0
            for score_doc in doc["scores"].values():
                sum_score += score_doc["score"]
            doc["sum"] = sum_score

    except Exception as e:
        return serialization.make_resp({"error_msg": f"参数错误:{e}"}, code=400)
    doc[f'done_{sp.id}'] = True
    task.get_mongo_group().save(doc)
    return serialization.make_resp({
        "scores": [doc["scores"][f'{score["id"]}'] for score in scores_list]
    }, code=200)


# 上传作业数据
@admin.route("/homework/upload", methods=['POST'])
@spider_jwt
def upload_task_auto():
    task = request.json
    data_list = list(task["data"])
    for d in data_list:
        task_id, student_id, data = d["task_id"], d["student_id"], d["data"]
        t = homeworks.find_by_id(task_id)
        if not t:
            return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
        user = users.find_by_student_id(student_id)
        if not user:
            return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
        if t.team_type == 0:
            # 个人作业
            task_team = user
        elif t.team_type == 1:
            # 结对作业
            task_team = user.pair
        elif t.team_type == 2:
            # 团队作业
            task_team = user.team
        else:
            return serialization.make_resp({"error_msg": "作业格式错误"}, code=400)
        if not task_team:
            return serialization.make_resp({"error_msg": "查询不到队伍信息"}, code=404)
        t.save_mongo_doc(task_team.id, data)
    return serialization.make_resp({"msg": "提交成功"}, code=200)


# 导出excel
@admin.route("/homework/<string:task_id>/excel", methods=['GET'])
@login_required("SuperAdmin", "Admin")
def homework_download(login_user: User, task_id):
    task = homeworks.find_by_id_force(task_id)
    if not task:
        return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    scores_list = task.get_all_scores()
    scores = task.get_scores()
    try:
        out = BytesIO()  # 实例化二进制数据
        workbook = xlsxwriter.Workbook(out)  # 创建一个Excel实例
        table = workbook.add_worksheet()
        table.write(0, 0, '得分点')
        table.write(1, 0, '详情')
        table.write(2, 0, '满分')
        for i, score in enumerate(scores):
            table.write(0, i + 1, f'{score.point}({score.max})')
            table.write(1, i + 1, f'{score.description}')
        table.write(0, len(scores) + 1, f'总计({task.score})')
        for row, doc in enumerate(list(scores_list)):
            table.write(row + 2, 0, f'{task.get_team_name_by_id(doc["id"])}')
            for col, score in enumerate(doc["scores"].values()):
                table.write(row + 2, col + 1, f'{score["score"]}')
            table.write(row + 2, len(scores) + 1, f'{doc["sum"]}')
        workbook.close()
        filename = f"{task.title}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.xlsx"
        file = make_response(out.getvalue())
        out.close()
        file.headers['Content-Type'] = "application/vnd.ms-excel"
        file.headers["Cache-Control"] = "no-cache"
        file.headers['Content-Disposition'] = "attachment; filename*=%s" % \
                                              filename.encode("utf-8").decode("latin1")
        return file
    except Exception as e:
        return serialization.make_resp({"error_msg": f"下载失败:{e}"}, code=500)

