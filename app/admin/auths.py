"""权限管理"""
from . import admin
from models.users import User
from servers import auths, users
from utils.middleware import login_required
from utils import serialization


# 权限添加
@admin.route("/auths/<string:auth_name>/<string:student_id>", methods=["POST"])
@login_required("SuperAdmin")
def add_auth(login_user: User, auth_name, student_id):
    student = users.find_by_student_id(student_id)
    if not student:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    return auths.add_auth_by_name(student, auth_name)


# 权限删除
@admin.route("/auths/<string:auth_name>/<string:student_id>", methods=["DELETE"])
@login_required("SuperAdmin")
def remove_auth(login_user: User, auth_name, student_id):
    student = users.find_by_student_id(student_id)
    if not student:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    return auths.remove_auth_by_name(student, auth_name)
