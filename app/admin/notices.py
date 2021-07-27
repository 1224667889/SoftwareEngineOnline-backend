"""通知管理"""
from models.users import User
from . import admin
from flask import request
from servers import notices
from utils.middleware import login_required


# 广播通知
@admin.route("/notices/broadcast", methods=['POST'])
@login_required("SuperAdmin", "Admin")
def broadcast_notices(login_user: User):
    title = request.form.get("title", "通知")
    message = request.form.get("message", "")
    host = login_user.name
    return notices.broadcast(title, message, host)


# 单播通知
@admin.route("/notice/<string:student_id>", methods=['POST'])
@login_required("SuperAdmin", "Admin")
def uni_cast_notices(login_user: User, student_id):
    title = request.form.get("title", "通知")
    message = request.form.get("message", "")
    host = login_user.name
    return notices.send(student_id, title, message, host)
