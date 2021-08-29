"""账号功能"""
from . import user
from flask import request
from models.users import User
from servers import users
from utils.middleware import login_required
from utils import serialization
from utils.middleware import generate_token
from utils.util import check_password


# 用户登录
@user.route('/login', methods=['POST'])
def user_login():
    student_id = request.form.get("student_id")
    password = request.form.get("password")
    return users.login(student_id, password)


# 刷新token
@user.route('/token', methods=['PUT'])
@login_required("SuperAdmin", "Admin", "Student")
def refresh_token(login_user: User):
    return serialization.make_resp({"token": generate_token(login_user), "detail": login_user.get_msg()}, code=200)


# 密码修改
@user.route('/password', methods=['PUT'])
@login_required("SuperAdmin", "Admin", "Student")
def change_password(login_user: User):
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    if check_password(new_password):
        return serialization.make_resp(
            {"error_msg": "密码只能由数字、大小写字母以及特殊符号@$!%*?&.构成，密码长度6~18位"},
            code=400)
    if login_user.change_password(old_password, new_password):
        return serialization.make_resp({"error_msg": "身份验证失败"}, code=401)
    return serialization.make_resp({"msg": "密码修改成功"}, code=200)


# 查看个人信息
@user.route('/detail', methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def check_detail(login_user: User):
    return serialization.make_resp({"detail": login_user.get_msg()}, code=200)
