"""用户"""
from utils.logger import logger
from app import db
from werkzeug.security import generate_password_hash, check_password_hash
from servers import auths
from models import auths


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(16), unique=True)                 # 学号
    password = db.Column(db.String(255))                               # 密码
    is_changed = db.Column(db.Boolean, default=0)                      # 是否修改密码

    name = db.Column(db.String(16))

    auths = db.relationship('Auth', backref='users', secondary=auths.users_auths, lazy='dynamic')
    notices = db.relationship('Notice', backref='user', lazy='dynamic')

    def add(self, student_id, name, auth_name="Student", commit=True):
        self.student_id = student_id
        self.name = name
        self.hash_password(student_id)
        try:
            db.session.add(self)
            # 多用户导入时，commit在路由函数处执行，可加快速度
            if commit:
                db.session.commit()
            self.auths.append(auths.find_by_name(auth_name))
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def verify_password(self, password):
        """验证密码正确性"""
        return check_password_hash(self.password, password)

    def hash_password(self, password):
        """生成密码"""
        self.password = generate_password_hash(password)

    def change_password(self, old_password, new_password):
        """修改密码"""
        if not self.verify_password(old_password):
            return 1        # 密码验证失败，提醒重新输入密码
        try:
            self.hash_password(new_password)
            self.is_changed = 1
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
        return None

    def refresh_password(self):
        """重置密码"""
        try:
            self.hash_password(self.student_id)
            self.is_changed = 0
            db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def get_msg(self):
        """获取用户基本信息"""
        return {
            "name": self.name,
            "student_id": self.student_id,
            "id": self.id
        }
