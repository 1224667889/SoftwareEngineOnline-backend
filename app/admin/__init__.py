"""管理模块"""
from flask import Blueprint

admin = Blueprint('admin', __name__)

from . import account
