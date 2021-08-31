"""作业批改"""
from models.users import User
from . import admin
from servers import homeworks
from utils.middleware import login_required
from utils import serialization
from flask import request
import time


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
    task = doc["task"]["html"]      # Todo: 分割函数
    return serialization.make_resp({"split": sp.get_msg(), "task": task}, code=200)


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
    except Exception as e:
        return serialization.make_resp({"error_msg": f"参数错误:{e}"}, code=400)
    doc[f'done_{sp.id}'] = True
    task.get_mongo_group().save(doc)
    return serialization.make_resp({"scores": [doc["scores"][f'{score["id"]}'] for score in scores_list]}, code=200)


# 上传作业数据
@admin.route("/homework/upload", methods=['POST'])
def upload_task_auto(login_user: User):
    # task = homeworks.find_by_id(task_id)
    # if not task:
    #     return serialization.make_resp({"error_msg": "作业不存在"}, code=404)
    return serialization.make_resp({"splits": task.get_splits()}, code=200)
