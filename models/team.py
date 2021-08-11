from app import db
from utils.logger import logger
import datetime


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True)        # 邀请码
    captain_id = db.Column(db.Integer)                   # 队长Id
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间

    students = db.relationship('User', backref='team', lazy='dynamic')

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
