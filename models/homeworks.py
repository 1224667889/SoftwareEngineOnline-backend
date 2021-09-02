from app import db
from utils.logger import logger
import datetime
from utils.util import create_safe_name, allow_document
from config import documents_path
from models.users import User
from models.auths import Auth
from models.pairs import Pair
from models.teams import Team
from app import mongoCli
from servers import users, pairs, teams


# 分割点
class Split(db.Model):
    __tablename__ = 'splits'
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255))

    task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    scores = db.relationship('Score', backref='scores', lazy='dynamic')

    def __init__(self, title):
        self.title = title

    def get_msg(self):
        return {
            "id": self.id,
            "title": self.title,
            "scores": [score.get_msg() for score in self.scores],
            "finished": self.get_finished_count()
        }

    def get_mongo_doc(self):
        group = self.get_mongo_group()
        return group.find_one({f'done_{self.id}': False})

    def get_finished_count(self):
        group = self.get_mongo_group()
        return group.count({f'done_{self.id}': True})

    def get_mongo_doc_by_id(self, doc_id):
        group = self.get_mongo_group()
        return group.find_one({"id": doc_id})

    def get_mongo_group(self):
        mongo_db = self.task.get_mongo_db()
        return mongo_db[f"{self.task.id}-{self.task.title}"]

    def get_mongo_db(self):
        # 0:单人;1:结对;2:团队
        if self.task.team_type == 2:
            return mongoCli["team"]
        elif self.task.team_type == 1:
            return mongoCli["pair"]
        else:
            return mongoCli["person"]


# 单项分数
class Score(db.Model):
    __tablename__ = 'scores'
    id = db.Column(db.Integer, primary_key=True)
    point = db.Column(db.String(15))
    description = db.Column(db.String(255))
    max = db.Column(db.Integer)

    # task_id = db.Column(db.Integer, db.ForeignKey('tasks.id'))
    split_id = db.Column(db.Integer, db.ForeignKey('splits.id'))

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
            "id": self.id,
            "point": self.point,
            "description": self.description,
            "max": self.max,
        }

    def create_doc(self):
        return {
            "point": self.point,
            "description": self.description,
            "max": self.max,
            "score": 0,
            "referee": "",
            "mark_at": 0
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
    url = db.Column(db.String(255))                 # 博客地址
    is_delete = db.Column(db.Boolean, default=False)    # 是否删除（软删除）
    weight = db.Column(db.Integer, default=0)       # 权重
    score = db.Column(db.Integer)                   # 总分：冗余减少计算量

    user_id = db.Column(db.Integer, db.ForeignKey('users.id'))

    documents = db.relationship('Document', backref='task', lazy='dynamic')
    splits = db.relationship('Split', backref='task', lazy='dynamic')

    def add(self,
            url: str,
            title: str,
            team_type: int,
            begin_at: datetime,
            deadline: datetime,
            over_at: datetime,
            weight: int,
            documents: list,
            splits: list,
            scores: list,
            host: User,
            commit=True):
        self.url = url
        self.title = title
        self.team_type = team_type
        self.begin_at = begin_at
        self.deadline = deadline
        self.over_at = over_at
        self.weight = weight
        self.score = 0
        self.user_id = host.id
        splits_list = []
        try:
            splits_list.append(Split("其他"))
            for split_title in splits:
                splits_list.append(Split(split_title))
            for score in scores:
                s = Score()
                e = s.add(score['point'], score['description'], score['max'])
                if e:
                    return e
                index = score.get("parent", 0)
                splits_list[index].scores.append(s)
                self.score += s.max
                # self.scores.append(s)
            [self.splits.append(sp) for sp in splits_list]
            for document in documents:
                if document:
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
            "url": self.url,
            "due": self.get_due(),
            "all": self.count_mongo(),
            "documents": [document.get_msg() for document in self.documents],
            "splits": [split.get_msg() for split in self.splits]        # <-按这个去切
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
            "scores": [score.get_msg() for score in self.get_scores()],
            "documents": [document.get_msg() for document in self.documents]
        }

    def get_scores(self):
        scores = []
        for split in self.splits:
            for score in split.scores:
                scores.append(score)
        return scores

    def get_splits(self):
        return [split.get_msg() for split in self.splits]

    def get_index(self):
        return {
            "id": self.id,
            "title": self.title,
            "begin_at": datetime.datetime.timestamp(self.begin_at),
            "deadline": datetime.datetime.timestamp(self.deadline),
            "state": self.get_status(),
            "due": self.get_due(),
            "all": self.count_mongo(),
        }

    def get_due(self):
        if self.team_type == 0:
            auth = db.session.query(Auth).filter_by(name="Student").first()
            return auth.users.count()
        elif self.team_type == 1:
            return db.session.query(Pair).count()
        elif self.team_type == 2:
            return db.session.query(Pair).count()
        return -1

    def get_status(self):
        now = datetime.datetime.now()
        if self.begin_at < now:
            return 0
        elif self.deadline < now:
            return 1
        elif self.over_at < now:
            return 2
        else:
            return 0

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

    def get_mongo_db(self):
        # 0:单人;1:结对;2:团队
        if self.team_type == 2:
            return mongoCli["team"]
        elif self.team_type == 1:
            return mongoCli["pair"]
        else:
            return mongoCli["person"]

    def get_mongo_group(self):
        mongo_db = self.get_mongo_db()
        return mongo_db[f"{self.id}-{self.title}"]

    def save_mongo_doc(self, doc_id, task: dict):
        group = self.get_mongo_group()
        try:
            doc = group.find_one({'id': doc_id})
            scores = {}
            for score in self.get_scores():
                scores[f'{score.id}'] = score.create_doc()
            dic = {
                "id": doc_id,
                "sum": 0,
                "max": self.score,
                "task": task,
                "scores": scores
            }
            for split in self.splits:
                dic[f'done_{split.id}'] = False
            if doc:
                doc.update(dic)
                group.save(doc)
            else:
                group.insert(dic)
            return None
        except Exception as e:
            logger.error(e)
            return e

    def count_mongo(self):
        group = self.get_mongo_group()
        return group.count()

    def get_doc_scores(self, doc_id):
        group = self.get_mongo_group()
        doc = group.find_one({"id": doc_id})
        if doc:
            return doc, doc["scores"]
        return None, None

    def get_doc_rank(self, doc_id):
        group = self.get_mongo_group()
        doc = group.find_one({"id": doc_id})
        if not doc:
            return None, None, None, None
        doc_list = list(group.find())
        doc_list = sorted(doc_list, key=lambda d: d["sum"], reverse=True)
        return doc, doc["scores"], doc_list.index(doc), len(doc_list)

    def get_all_scores(self):
        group = self.get_mongo_group()
        return list(group.find())

    def get_team_name_by_id(self, team_id):
        if self.team_type == 0:
            # 个人作业
            task_team = users.find_by_id(team_id)
        elif self.team_type == 1:
            # 结对作业
            task_team = pairs.find_by_id(team_id)
        elif self.team_type == 2:
            # 团队作业
            task_team = teams.find_by_id(team_id)
        else:
            return None
        return task_team.name



