from app import db
from models.auths import Auth
from servers import users
from utils import serialization


def find_by_id(auth_id=4):
    return db.session.query(Auth).filter_by(id=auth_id).first()


def find_by_name(auth_name="Student"):
    return db.session.query(Auth).filter_by(name=auth_name).first()


def add_auth_by_name(student_id, auth_name):
    student = users.find_by_student_id(student_id)
    if not student:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    auth = find_by_name(auth_name)
    if not auth:
        return serialization.make_resp({"error_msg": "未定义权限"}, code=404)
    if auth in student.auths:
        serialization.make_resp({"error_msg": "用户已有该权限"}, code=400)
    err = student.add_auth(auth)
    if err:
        return serialization.make_resp({"error_msg": "添加失败"}, code=500)
    return serialization.make_resp({"msg": "添加成功"}, code=200)


def remove_auth_by_name(student_id, auth_name):
    student = users.find_by_student_id(student_id)
    if not student:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    auth = find_by_name(auth_name)
    if not auth:
        return serialization.make_resp({"error_msg": "未定义权限"}, code=404)
    if auth not in student.auths:
        serialization.make_resp({"error_msg": "用户无该权限"}, code=404)
    err = student.remove_auth(auth)
    if err:
        return serialization.make_resp({"error_msg": "添加失败"}, code=500)
    return serialization.make_resp({"msg": "添加成功"}, code=200)

