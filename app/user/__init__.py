"""用户模块"""
from flask import Blueprint
from . import *
user = Blueprint('user', __name__)


