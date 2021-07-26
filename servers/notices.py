from app import db
from utils import serialization
from utils.middleware import generate_token
from models.notices import Notice
from models.users import User


def find_by_id(notice_id):
    """id查询-唯一"""
    return db.session.query(Notice). \
        filter_by(id=notice_id).first()


def find_all():
    """查询全部"""
    return Notice.query.all()         # 需消耗较大内存，但是方便


def find_by_user_read(user: User, read=-1):
    """关联获取(常用)"""
    if read == -1:      # -1获取全部
        return user.notices
    return user.notices.filter_by(read=read).all()
