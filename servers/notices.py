from app import db
from models.notices import Notice
from models.users import User
from servers import users
from utils import serialization


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


def broadcast(title, message, host):
    """广播消息"""
    students = users.find_all()
    for student in students:
        err = Notice.add(student, title, message, host)
        if err:
            db.session.rollback()
            return serialization.make_resp({"error_msg": "广播时出错，详情请查看错误日志"}, code=500)
        db.session.commit()
    return serialization.make_resp({"msg": "广播完成"}, code=200)


def send(student_id, title, message, host):
    """单播消息"""
    student = users.find_by_student_id(student_id)
    err = Notice.add(student, title, message, host, commit=True)
    if err:
        db.session.rollback()
        return serialization.make_resp({"error_msg": "消息发送时出错，详情请查看错误日志"}, code=500)
    return serialization.make_resp({"msg": "消息发送完成"}, code=200)