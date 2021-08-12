from app import db
from utils.logger import logger
import datetime


# 没法用继承，父类也会被创建，有点冗余
class TeamProportion(db.Model):
    __tablename__ = 'team_proportions'
    id = db.Column(db.Integer, primary_key=True)
    update_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())     # 更新时间
    job = db.Column(db.String(255))     # 分工
    rate = db.Column(db.Float)          # 占比

    team_id = db.Column(db.Integer, db.ForeignKey('teams.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, job="未分配", rate=0):
        self.job = job
        self.rate = rate

    def get_msg(self):
        return {
            "id": self.user_id,     # 返回user的id
            "job": self.job,
            "rate": self.rate,
            "name": self.user.name,
            "student_id": self.user.student_id,
            "updated": datetime.datetime.timestamp(self.update_at)
        }

    def delete(self):
        try:
            db.session.delete(self)
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e


class PairProportion(db.Model):
    __tablename__ = 'pair_proportions'
    id = db.Column(db.Integer, primary_key=True)
    update_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())     # 更新时间
    job = db.Column(db.String(255))     # 分工
    rate = db.Column(db.Float)          # 占比

    pair_id = db.Column(db.Integer, db.ForeignKey('pairs.id'))
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def __init__(self, job="未分配", rate=0):
        self.job = job
        self.rate = rate

    def get_msg(self):
        return {
            "id": self.user_id,     # 返回user的id
            "job": self.job,
            "rate": self.rate,
            "name": self.user.name,
            "student_id": self.user.student_id,
            "updated": datetime.datetime.timestamp(self.update_at)
        }

    def delete(self):
        try:
            db.session.delete(self)
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
