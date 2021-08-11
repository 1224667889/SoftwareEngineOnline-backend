from app import db
from utils.logger import logger
import datetime


class HistoryNotice(db.Model):
    __tablename__ = 'history_notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))               # 标题
    message = db.Column(db.String(255))             # 信息
    host = db.Column(db.String(16))                 # 来源
    to = db.Column(db.String(16))                   # 类型：""为广播，其他为按学号单播
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间

    def add(self, title, message, host, to, commit=True):
        self.title = title
        self.message = message
        self.host = host
        self.to = to
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
            "title": self.title,
            "host": self.host,
            "to": self.to,
            "confirmed": self.confirmed_at
        }

    def get_detail(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "host": self.host,
            "to": self.to,
            "confirmed": self.confirmed_at
        }
