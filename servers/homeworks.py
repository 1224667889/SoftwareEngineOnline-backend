from app import db
from models.homeworks import Task, Document
import datetime


def upload_document(file):
    d = Document()
    return d, d.add(file, commit=True)


def find_document_u_name(u_name):
    return db.session.query(Document).\
        filter_by(u_name=u_name).first()


def find_by_id(task_id):
    """id查询-唯一"""
    return db.session.query(Task).\
        filter_by(id=task_id).first()


def find_by_team_type(team_type):
    return db.session.query(Task).\
        filter_by(team_type=team_type).all()


def find_by_task_type(task_type):
    return db.session.query(Task).\
        filter_by(task_type=task_type).all()


def find_by_team_and_task_type(team_type=-1, task_type=-1):
    tasks = db.session.query(Task)
    if team_type != -1:
        tasks = tasks.filter_by(team_type=team_type)
    if task_type != -1:
        tasks = tasks.filter_by(team_type=task_type)
    return tasks.all()


def find_by_team_type_page(team_type, page_number=1, page_size=10, keyword=""):
    pagination = db.session.query(Task). \
        filter_by(team_type=team_type). \
        filter(Task.name.like(f'%{keyword}%')) \
        .paginate(page_number, per_page=page_size)
    return pagination.items, pagination.pages


def find_by_task_type_type(task_type, page_number=1, page_size=10, keyword=""):
    pagination = db.session.query(Task). \
        filter_by(task_type=task_type). \
        filter(Task.name.like(f'%{keyword}%')) \
        .paginate(page_number, per_page=page_size)
    return pagination.items, pagination.pages


def find_by_team_and_task_type_page(team_type=-1, task_type=-1, page_number=1, page_size=10, keyword=""):
    tasks = db.session.query(Task)
    if team_type != -1:
        tasks = tasks.filter_by(team_type=team_type)
    if task_type != -1:
        tasks = tasks.filter_by(team_type=task_type)
    pagination = tasks.filter(Task.name.like(f'%{keyword}%')) \
        .paginate(page_number, per_page=page_size)
    return pagination.items, pagination.pages
