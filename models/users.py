"""用户"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from utils import serialization
from .auths import users_auths
from utils.middleware import generate_token


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, unique=True)                 # 学号
    password = db.Column(db.String(255))                            # 密码

    name = db.Column(db.String(16))
    # Todo: 其他学生信息

    auths = db.relationship('Auth', backref='users', secondary=users_auths, lazy='dynamic')

    def verify_password(self, password):
        """验证密码正确性"""
        return check_password_hash(self.password, password)

    def hash_password(self, password):
        """生成密码"""
        self.password = generate_password_hash(password)


def find_by_id(user_id):
    """id查询-唯一"""
    return db.session.query(User).filter_by(id=user_id).first()


def find_by_student_id(student_id):
    """学号查询-唯一"""
    return db.session.query(User).filter_by(student_id=student_id).first()

# Todo: 全字段模糊查询


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
        return serialization.make_resp({"token": token}, code=200)
    return serialization.make_resp({"error_msg": "账号或密码错误"}, code=400)

