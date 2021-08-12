"""通知管理"""
from models.users import User
from . import admin
from flask import request
from servers import notices
from utils.middleware import login_required
from utils import serialization


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

# 获取历史通知
@admin.route('/notice/history/<string:notice_id>', methods=['GET'])
@login_required("SuperAdmin", "Admin")
def check_notices(login_user: User, notice_id):
    history_notice = notices.find_history_by_id(notice_id)
    return serialization.make_resp(
        {"notice": history_notice.get_detail()},
        code=200
    )

# 获取历史通知列表
@admin.route('/notice/history/index', methods=['GET'])
@login_required("SuperAdmin", "Admin")
def index_history_notices(login_user: User):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    history_notices, total_page = notices.get_history(page_number, page_size)
    return serialization.make_resp(
        {"notices": [history_notice.get_msg() for history_notice in history_notices], "total_page": total_page},
        code=200
    )
