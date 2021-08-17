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
    if not title:
        return serialization.make_resp({"error_msg": "未填写标题"}, code=400)
    # Todo: 发布作业

