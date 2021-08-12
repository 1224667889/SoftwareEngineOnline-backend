from app import db
from utils import serialization
from utils.middleware import generate_token
from models.users import User


def find_by_id(user_id):
    """id查询-唯一"""
    return db.session.query(User).\
        filter_by(id=user_id).first()


def find_by_student_id(student_id):
    """学号查询-唯一"""
    return db.session.query(User).\
        filter_by(student_id=student_id).first()


def find_by_page(page_number=1, page_size=10, keyword=""):
    pagination = User.query. \
        filter(User.name.like(f'%{keyword}%')) \
        .paginate(page_number, per_page=page_size)
    return pagination.items, pagination.pages


def find_all():
    return User.query.all()         # 需消耗较大内存，但是方便


def login(student_id, password):
    """登录并返回token"""
    if not student_id:          # Todo: 使用正则进行验证
        return serialization.make_resp({"error_msg": "缺少学号"}, code=400)
    if not password:
        return serialization.make_resp({"error_msg": "缺少密码"}, code=400)
    user = find_by_student_id(student_id)
    if not user:
        return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
    if user.verify_password(password):
        token = generate_token(user)
        return serialization.make_resp({"token": token, "detail": user.get_msg()}, code=200)
    return serialization.make_resp({"error_msg": "账号或密码错误"}, code=400)
