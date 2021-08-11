from app import db
from utils.logger import logger
import datetime


class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    task_type = db.Column(db.Integer, default=0)    # 0:其他;1:oj;2:博客
    team_type = db.Column(db.Integer, default=0)    # 0:单人;1:结对;2:团队
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间

    def add(self, commit=True):

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
            "id": self.id,

        }
