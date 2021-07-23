"""用户管理"""
from utils.logger import logger
from . import admin
from flask import request
import xlrd
from utils import serialization
from models import users
from models import auths
from app import db
from utils.middleware import login_required


# 用户名单导入
@admin.route("/students/upload", methods=['POST'])
@login_required("SuperAdmin")
def students_upload():
    # # 测试代码
    # db.drop_all()
    # db.create_all()
    # auths.Auth().add("SuperAdmin", "老板")
    # auths.Auth().add("Admin", "管理员")          # 我们
    # auths.Auth().add("Group Leader", "组长")     # 小组组长
    # auths.Auth().add("Student", "学生")          # 所有学生（包括我们）
    # auths.Auth().add("Fish Monster", "摸鱼怪")   # 我
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
            err = users.User().add(student_id, name, commit=False)
            if err:
                db.session.rollback()
                return serialization.make_resp({"error_msg": "导入出错，请检查文件"}, code=500)
        db.session.commit()     # 上传完成后统一提交session，节约消耗
        return serialization.make_resp({"msg": "用户导入成功"}, code=200)
    return serialization.make_resp({"error_msg": "文件不符合要求"}, code=400)


# 密码重置
@admin.route("/password/refresh", methods=["PUT"])
@login_required("SuperAdmin", "Admin")
def refresh_password():
    student_id = request.form.get("student_id")
    user = users.find_by_student_id(student_id)
    if user.refresh_password():
        return serialization.make_resp({"error_msg": "重置密码失败，请联系管理员"}, code=500)
    return serialization.make_resp({"msg": user.get_msg()}, code=200)
