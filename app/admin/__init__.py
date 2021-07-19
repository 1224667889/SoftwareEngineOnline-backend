"""管理模块"""
from flask import Blueprint
from . import *
admin = Blueprint('admin', __name__)
