"""权限管理"""
from . import admin
from models.users import User
from servers import auths
from utils.middleware import login_required

# 权限添加
@admin.route("/auths/<string:auth_name>/<string:student_id>", methods=["POST"])
@login_required("SuperAdmin")
def add_auth(login_user: User, auth_name, student_id):
    return auths.add_auth_by_name(student_id, auth_name)

# 权限删除
@admin.route("/auths/<string:auth_name>/<string:student_id>", methods=["POST"])
@login_required("SuperAdmin")
def add_auth(login_user: User, auth_name, student_id):
    return auths.remove_auth_by_name(student_id, auth_name)
