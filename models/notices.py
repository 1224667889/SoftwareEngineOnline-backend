from app import db
from utils.logger import logger


class Notice(db.Model):
    __tablename__ = 'notices'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))               # 标题
    message = db.Column(db.String(255))             # 信息
    host = db.Column(db.String(16))                 # 来源
    read = db.Column(db.Boolean, default=0)         # 已读?

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    def add(self, user, title, message, host, commit=False):
        self.title = title
        self.message = message
        self.host = host
        try:
            user.notices.append(self)
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
            "read": self.read,
        }

    def get_msg_detail(self):
        return {
            "id": self.id,
            "title": self.title,
            "message": self.message,
            "host": self.host,
            "read": self.read,
            "user_id": self.user_id
        }

    def put_read(self):
        if self.read == 0:
            self.read = 1
            db.session.commit()
        return self.get_msg_detail()
