from app import db
from utils.logger import logger
import datetime
from utils.util import create_uuid
from config import MaxPair
from models.proportions import PairProportion
from models.notices import Notice


class Pair(db.Model):
    __tablename__ = 'pairs'
    id = db.Column(db.Integer, primary_key=True)
    code = db.Column(db.String(255), unique=True)        # 邀请码
    confirmed_at = db.Column(db.DateTime, index=True, default=datetime.datetime.now())  # 创建时间
    name = db.Column(db.String(255), unique=True)

    captain_id = db.Column(db.Integer)
    students = db.relationship('User', backref='pair', lazy='dynamic')
    proportions = db.relationship('PairProportion', backref='pair', lazy='dynamic')

    def add(self, captain, name, commit=True):
        if captain.pair:
            return 1    # 已有队伍，不能再加入其他队伍
        self.code = create_uuid()   # 36位
        self.name = name
        self.captain_id = captain.id
        try:
            self.students.append(captain)
            p = PairProportion()
            self.proportions.append(p)
            captain.pair_proportions.append(p)
            db.session.add(self)
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def join(self, student, commit=True):
        if student.pair:
            return 1    # 已有队伍，不能再加入其他队伍
        if len(self.students.all()) >= MaxPair:
            return 2    # 队伍已满

        try:
            self.students.append(student)
            p = PairProportion()
            self.proportions.append(p)
            student.pair_proportions.append(p)
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
            "confirmed": datetime.datetime.timestamp(self.confirmed_at),
            "members": [p.get_msg() for p in self.proportions],
            "captain": self.get_captain().get_msg()
        }

    def delete(self):
        for proportion in self.proportions:
            e = proportion.delete()
            if e:
                return e
        for student in self.students:
            Notice().add(
                student,
                "[结对系统]队伍解散",
                "您的队伍被队长解散",
                "系统消息",
                commit=False
            )
        try:
            db.session.delete(self)
            db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def set_name(self, name, commit=True):
        for student in self.students:
            Notice().add(
                student,
                "[结对系统]名称修改",
                "您的队伍名称更变为: " + name,
                "系统消息",
                commit=False
            )
        try:
            self.name = name
            if commit:
                db.session.commit()
            return None
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e

    def set_proportions(self, proportions):
        for student in self.students:
            Notice().add(
                student,
                "[结对系统]分工变动",
                "队长改变了分工或分配情况，请确认。",
                "系统消息",
                commit=False
            )
        try:
            for proportion in proportions:
                p = self.proportions.filter_by(user_id=proportion.get("id", 0)).first()
                if not p:
                    return 1
                job = proportion.get("job", "")
                rate = proportion.get("rate", -1)
                if job:
                    p.job = job
                    p.update_at = datetime.datetime.now()
                if rate >= 0:
                    p.rate = rate
                    p.update_at = datetime.datetime.now()
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
        return None

    def leave_msg(self, user):
        try:
            for student in self.students:
                Notice().add(
                    student,
                    "[结对系统]成员离开",
                    user.name + " 退出了团队",
                    "系统消息",
                    commit=False
                )
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
        return None

    def set_captain(self, user):
        if user not in self.students:
            return 1
        if user == self.get_captain():
            return 2
        try:
            self.captain_id = user.id
            for student in self.students:
                Notice().add(
                    student,
                    "[结对系统]移交队长",
                    user.name + " 成为了新的队长",
                    "系统消息",
                    commit=False
                )
            db.session.commit()
        except Exception as e:
            logger.error(e)
            db.session.rollback()
            return e
        return None
