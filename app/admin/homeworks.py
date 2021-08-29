"""作业管理"""
from models.users import User
from . import admin
from flask import request
from servers import homeworks
from utils.middleware import login_required
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
    title = request.json.get("title", "", type=str)
    task_type = request.json.get("task_type", -1, type=int)     # 0:其他;1:oj;2:博客
    team_type = request.json.get("team_type", -1, type=int)     # 0:单人;1:结对;2:团队
    if task_type > 2:
        task_type = -1
    if team_type > 2:
        team_type = -1
    # begin_at
    # deadline
    # over_at
    # document_id
    weight = request.json.get("weight", -1, type=int)
    scores = request.json.get("scores")
    if task_type == -1 or team_type == -1:
        return serialization.make_resp({"error_msg": "类型错误"}, code=400)
    if not title:
        return serialization.make_resp({"error_msg": "未填写标题"}, code=400)

