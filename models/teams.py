from app import db
from utils.logger import logger
import datetime
from utils.util import create_uuid
from config import MaxTeam
from models.proportions import TeamProportion


class Team(db.Model):
    __tablename__ = 'teams'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True)        # 邀请码
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间
    name = db.Column(db.String(255), unique=True)

    captain_id = db.Column(db.Integer)
    students = db.relationship('User', backref='team', lazy='dynamic')
    proportions = db.relationship('TeamProportion', backref='team', lazy='dynamic')

    def add(self, captain, name, commit=True):
        self.code = create_uuid()   # 36位
        self.name = name
        self.captain_id = captain.id
        try:
            self.students.append(captain)
            p = TeamProportion()
            self.proportions.append(p)
            captain.team_proportions.append(p)
            db.session.add(self)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def join(self, student, commit=True):
        if student.team:
            return 1    # 已有队伍，不能再加入其他队伍
        if len(self.students.all()) >= MaxTeam:
            return 2    # 队伍已满

        try:
            self.students.append(student)
            p = TeamProportion()
            self.proportions.append(p)
            student.team_proportions.append(p)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def get_captain(self):
        return self.students.filter_by(id=self.captain_id).first()

    def get_students(self):
        return self.students.all()

    def get_msg(self):
        return {
            "id": self.id,
            "name": self.name,
            "code": self.code,
            "confirmed": self.confirmed_at,

        }

    def delete(self):
        for proportion in self.proportions:
            e = proportion.delete()
            if e:
                return e
        try:
            db.session.delete(self)
            db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
