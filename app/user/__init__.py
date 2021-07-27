"""用户模块"""
from flask import Blueprint

user = Blueprint('user', __name__)

from . import account, notices
