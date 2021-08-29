from app import db
from models.homeworks import Task, Document
import datetime
from models.users import User


def create_homework(title: str,
                    team_type: int,
                    begin_at: datetime,
                    deadline: datetime,
                    over_at: datetime,
                    weight: int,
                    documents: list,
                    scores: list,
                    host: User):
    task = Task()
    return task, task.add(title, team_type, begin_at, deadline, over_at, weight, documents, scores, host)


def upload_document(file):
    d = Document()
    return d, d.add(file, commit=True)


def find_document_u_name(u_name):
    return db.session.query(Document).\
        filter_by(u_name=u_name).first()


def find_by_id(task_id):
    """id查询-唯一"""
    return db.session.query(Task).\
        filter_by(is_delete=False).\
        filter_by(id=task_id).first()


def find_by_id_force(task_id):
    """id查询-唯一"""
    return db.session.query(Task). \
        filter_by(id=task_id).first()


def find_by_team_type(team_type):
    return db.session.query(Task). \
        filter_by(is_delete=False). \
        filter_by(team_type=team_type).all()


def find_by_team_type_page(team_type, page_number=1, page_size=10, keyword="", is_delete=-1):
    tasks = db.session.query(Task)
    if is_delete != -1:
        tasks = tasks.filter_by(is_delete=is_delete)
    if team_type != -1:
        tasks = tasks.filter_by(team_type=team_type)
    pagination = tasks.\
        filter(Task.title.like(f'%{keyword}%')).\
        paginate(page_number, per_page=page_size)
    return pagination.items, pagination.pages

