"""管理模块"""
from flask import Blueprint

test = Blueprint('test', __name__)

from . import abab
