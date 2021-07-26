"""账号功能"""
from . import user
from flask import request
from models import users
from servers import users
from utils.middleware import login_required
from utils import serialization


# 用户登录
@user.route('/login', methods=['POST'])
def user_login():
    student_id = request.form.get("student_id")
    password = request.form.get("password")
    return users.login(student_id, password)


# 密码修改
@user.route('/password', methods=['PUT'])
@login_required("SuperAdmin", "Admin", "Student")
def change_password(login_user: users.User):
    old_password = request.form.get("old_password")
    new_password = request.form.get("new_password")
    # Todo: 正则验证格式   ！重要！
    if login_user.change_password(old_password, new_password):
        return serialization.make_resp({"error_msg": "身份验证失败"}, code=400)
    return serialization.make_resp({"msg": "密码修改成功"}, code=200)


# 查看个人信息
@user.route('/detail', methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def check_detail(login_user: users.User):
    return serialization.make_resp({"msg": login_user.get_msg()}, code=200)
