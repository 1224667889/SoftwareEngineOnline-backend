"""账号功能"""
from . import user
from flask import request
from models.users import *


# 用户登录
@user.route('/login', methods=['POST'])
def user_login():
    student_id = request.form.get("student_id")
    password = request.form.get("password")
    return login(student_id, password)
