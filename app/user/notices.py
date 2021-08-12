"""通知功能"""
from . import user
from flask import request
from models.users import User
from servers import notices
from utils.middleware import login_required
from utils import serialization


# 获取通知
@user.route('/notice/<string:notice_id>', methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def check_notices(login_user: User, notice_id):
    notice = notices.find_by_id(notice_id)
    if notice not in login_user.notices:
        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
    return serialization.make_resp(
        {"notice": notice.put_read()},
        code=200
    )


# 获取通知列表
@user.route('/notice/index', methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def index_notices(login_user: User):
    read = request.args.get("read", -1, type=int)
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)

    notices_, total_page = notices.find_by_user_read(login_user, read, page_number, page_size)
    return serialization.make_resp(
        {"notices": [notice.get_msg() for notice in notices_], "total_page": total_page},
        code=200
    )
