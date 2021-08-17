from app import db
from utils.logger import logger
import datetime
from utils.util import create_safe_name, allow_document
from config import documents_path


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


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))
    task_type = db.Column(db.Integer, default=0)    # 0:其他;1:oj;2:博客
    team_type = db.Column(db.Integer, default=0)    # 0:单人;1:结对;2:团队
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间
    begin_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())      # 开始时间
    deadline = db.Column(db.DateTime, index=True, default=datetime.datetime.now())      # 结束时间
    over_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())       # 公示时间
    weight = db.Column(db.Integer, default=0)       # 权重
    score = db.Column(db.Integer)                   # 总分：冗余减少计算量

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    scores = db.relationship('Score', backref='task', lazy='dynamic')
    documents = db.relationship('Document', backref='task', lazy='dynamic')

    def add(self, title: str,
            task_type: int,
            team_type: int,
            begin_at: datetime,
            deadline: datetime,
            over_at: datetime,
            weight: int,
            document: Document,
            scores: list,
            commit=True):
        self.title = title
        self.task_type = task_type
        self.team_type = team_type
        self.begin_at = begin_at
        self.deadline = deadline
        self.over_at = over_at
        self.weight = weight
        try:
            for score in scores:
                s = Score()
                e = s.add(score['point'], score['description'], score['max'])
                if e:
                    return e
                self.scores.append(s)
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
            "task_type": self.task_type,
            "team_type": self.team_type,
            "confirmed_at": self.confirmed_at,
            "begin_at": self.begin_at,
            "over_at": self.over_at,
            "deadline": self.deadline,
            "publisher": self.user.name,
            "weight": self.weight,
            "score": self.score,
        }

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