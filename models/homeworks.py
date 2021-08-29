from app import db
from utils.logger import logger
import datetime
from utils.util import create_safe_name, allow_document
from config import documents_path
from models.users import User


# 单项分数
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    point = db.Column(db.String(15))
    description = db.Column(db.String(255))
    max = db.Column(db.Integer)

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def add(self, point: str, description: str, max: int, commit=False):
        self.point = point
        self.description = description
        self.max = max
        try:
            db.session.add(self)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def get_msg(self):
        return {
            "point": self.point,
            "description": self.description,
            "max": self.max
        }


# 附件
class Document(db.Model):
    __tablename__ = 'documents'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255))                        # 原本名称(不唯一)
    u_name = db.Column(db.String(255), unique=True)         # 存储名称(唯一)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))

    def get_msg(self):
        return {
            "u_name": self.u_name,
            "name": self.name
        }

    def add(self, document, commit=True):
        self.name = document.filename
        self.u_name = create_safe_name()
        suffix = self.name.split('.')[-1]
        if not allow_document(suffix):
            return 1
        try:
            document.save(documents_path + self.u_name)  # 保存到本地
            db.session.add(self)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e


# 作业
class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    team_type = db.Column(db.Integer, default=0)    # 0:单人;1:结对;2:团队
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间
    begin_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())      # 开始时间
    deadline = db.Column(db.DateTime, index=True, default=datetime.datetime.now())      # 结束时间
    over_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())       # 公示时间
    is_delete = db.Column(db.Boolean, default=False)    # 是否删除（软删除）
    weight = db.Column(db.Integer, default=0)       # 权重
    score = db.Column(db.Integer)                   # 总分：冗余减少计算量

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    scores = db.relationship('Score', backref='task', lazy='dynamic')
    documents = db.relationship('Document', backref='task', lazy='dynamic')

    def add(self, title: str,
            team_type: int,
            begin_at: datetime,
            deadline: datetime,
            over_at: datetime,
            weight: int,
            documents: list,
            scores: list,
            host: User,
            commit=True):
        self.title = title
        self.team_type = team_type
        self.begin_at = begin_at
        self.deadline = deadline
        self.over_at = over_at
        self.weight = weight
        self.score = 0
        self.user_id = host.id
        try:
            for score in scores:
                s = Score()
                e = s.add(score['point'], score['description'], score['max'])
                if e:
                    return e
                self.score += s.max
                self.scores.append(s)
            for document in documents:
                self.documents.append(document)
            db.session.add(self)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def get_msg(self):
        return {
            "id": self.id,
            "team_type": self.team_type,
            "title": self.title,
            "confirmed_at": datetime.datetime.timestamp(self.confirmed_at),
            "begin_at": datetime.datetime.timestamp(self.begin_at),
            "over_at": datetime.datetime.timestamp(self.over_at),
            "deadline": datetime.datetime.timestamp(self.deadline),
            "publisher": self.user.name,
            "weight": self.weight,
            "sum": self.score,
            "is_delete": self.is_delete,
            "scores": [score.get_msg() for score in self.scores],
            "documents": [document.get_msg() for document in self.documents]
        }

    def get_msg_safe(self):
        return {
            "id": self.id,
            "team_type": self.team_type,
            "title": self.title,
            "begin_at": datetime.datetime.timestamp(self.begin_at),
            "over_at": datetime.datetime.timestamp(self.over_at),
            "deadline": datetime.datetime.timestamp(self.deadline),
            "weight": self.weight,
            "sum": self.score,
            "scores": [score.get_msg() for score in self.scores],
            "documents": [document.get_msg() for document in self.documents]
        }

    def get_index(self):
        return {
            "id": self.id,
            "title": self.title,
            "begin_at": datetime.datetime.timestamp(self.begin_at),
            "deadline": datetime.datetime.timestamp(self.deadline),
        }

    def change_state(self):
        try:
            self.is_delete = not self.is_delete
            db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def change_weight(self, weight: int):
        try:
            self.weight = weight
            db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def upload_homework(self, homework):
        now = datetime.datetime.now()
        if now > self.deadline + datetime.timedelta(days=3):
            return "你完了"
        if now > self.deadline + datetime.timedelta(days=2):
            return "凉一半"
        if now > self.deadline + datetime.timedelta(days=1):
            return "没完全凉"
        if now > self.deadline:
            return "overtime"
        if now > self.begin_at:
            return "success"
        return "not begin"
