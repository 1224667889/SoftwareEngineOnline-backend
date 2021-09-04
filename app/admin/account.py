"""用户管理"""
from utils.logger import logger
from . import admin
from flask import request
import xlrd
from utils import serialization
from models.users import User
from servers import users
from app import db
from utils.middleware import login_required


# 用户名单导入
@admin.route("/students/upload", methods=['POST'])
@login_required("SuperAdmin")
def students_upload(login_user: User):
    # 重置数据库
    db.drop_all()
    db.create_all()
    from models.auths import Auth
    Auth().add("SuperAdmin", "老板")
    Auth().add("Admin", "管理员")          # 我们
    Auth().add("Student", "学生")          # 所有学生（包括我们）
    User().add("66666666", "老板", auth_name="SuperAdmin")
    try:
        file = request.files['file']
        data = xlrd.open_workbook(file_contents=file.read())
        table = data.sheets()[0]
    except Exception as e:
        logger.error(e)
        return serialization.make_resp({"error_msg": "文件不符合要求"}, code=400)
    if data.sheet_loaded(data.sheet_names()[0]):
        for i in range(3, table.nrows):
            student_id, name = [cell.value for cell in table.row_slice(i)][0:2]
            err = User().add(student_id, name, commit=False)
            if err:
                db.session.rollback()
                return serialization.make_resp({"error_msg": "导入出错，请检查文件"}, code=500)
        db.session.commit()     # 上传完成后统一提交session，节约消耗
        return serialization.make_resp({"msg": "用户导入成功"}, code=200)
    return serialization.make_resp({"error_msg": "文件不符合要求"}, code=400)


# 密码重置
@admin.route("/password/<string:student_id>", methods=["PUT"])
@login_required("SuperAdmin", "Admin")
def refresh_password(login_user: User, student_id):
    user = users.find_by_student_id(student_id)
    if not user:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    if user.refresh_password():
        return serialization.make_resp({"error_msg": "重置密码失败，请联系管理员"}, code=500)
    return serialization.make_resp({"detail": user.get_msg()}, code=200)


# 全员密码重置
@admin.route("/password", methods=["PUT"])
@login_required("SuperAdmin")
def refresh_all_password(login_user: User):
    for user in users.find_all():
        if user.refresh_password():
            return serialization.make_resp({"error_msg": "重置密码失败，请联系管理员"}, code=500)
    return serialization.make_resp({"msg": "重置成功"}, code=200)


# 用户列表-分页查询
@admin.route("/users/detail", methods=["GET"])
@login_required("SuperAdmin", "Admin")
def check_users_detail(login_user: User):
    page_number = request.args.get('page_number', 1, type=int)
    page_size = request.args.get('page_size', 10, type=int)
    keyword = request.args.get('keyword', "")
    students, total_page = users.find_by_page(page_number, page_size, keyword)
    return serialization.make_resp({"students": [student.get_msg() for student in students], "total_page": total_page},
                                   code=200)


# 按学号获取用户
@admin.route("/user/<string:student_id>", methods=["GET"])
@login_required("SuperAdmin", "Admin")
def user_detail(login_user: User, student_id):
    student = users.find_by_student_id(student_id)
    if not student:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    return serialization.make_resp({"student": student.get_msg()}, code=200)


# 新增用户
@admin.route("/user", methods=["POST"])
@login_required("SuperAdmin", "Admin")
def add_new_user(login_user: User):
    student_id = request.form.get("student_id")
    name = request.form.get("name")
    user = User()
    err = user.add(student_id, name, commit=True)
    if err:
        db.session.rollback()
        return serialization.make_resp({"error_msg": "导入出错，请检查文件"}, code=500)
    return serialization.make_resp({"student": user.get_msg()}, code=200)
