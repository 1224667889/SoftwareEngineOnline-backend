"""通知功能"""
from . import user
from flask import request
from models import users
from servers import users
from servers import notices
from utils.middleware import login_required
from utils import serialization


# 获取通知
@user.route('/notices', methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def check_notices(login_user: users.User):
    read = request.args.get("read", -1, type=int)
    notices_ = notices.find_by_user_read(login_user, read)
    return serialization.make_resp(
        {"msg": [notice.get_msg_detail() for notice in notices_]},
        code=200
    )
