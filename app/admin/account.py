"""用户管理"""
from . import admin
from flask import request
import xlrd
from utils import serialization


# 用户名单导入
@admin.route("/students/upload", methods=['POST'])
def students_upload():
    from app import db
    db.create_all()
    return "666"

