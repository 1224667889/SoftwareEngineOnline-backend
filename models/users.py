"""用户"""
from app import db
from werkzeug.security import generate_password_hash, check_password_hash


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, unique=True)                 # 学号
    password = db.Column(db.String(255))                            # 密码

    name = db.Column(db.String(16))
    # Todo: 其他学生信息

    def verify_password(self, password):
        """验证密码正确性"""
        return check_password_hash(self.password, password)

    def hash_password(self, password):
        """生成密码"""
        self.password = generate_password_hash(password)

    def register(self, **kwargs):
        self.hash_password(kwargs.password)


def find_by_id(user_id):
    """id查询-唯一"""
    return db.session.query(User).filter_by(id=user_id).first()


def find_by_student_id(student_id):
    """学号查询-唯一"""
    return db.session.query(User).filter_by(student_id=student_id).first()

# Todo: 全字段模糊查询
