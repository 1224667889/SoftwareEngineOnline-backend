"""账号功能"""
from . import user
from flask import request
from utils import serialization


@user.route('/login', methods=['POST'])
def user_login():
    student_id = request.form.get("student_id")
    password = request.form.get("password")
    if not student_id:          # Todo: 使用正则进行验证
        return serialization.make_resp({"error_msg": "缺少学号"}, code=400)
    if not password:
        return serialization.make_resp({"error_msg": "缺少密码"}, code=400)
    return serialization.make_resp({"token": "abab"}, code=200)
