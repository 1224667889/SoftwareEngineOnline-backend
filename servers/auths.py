from app import db
from models.auths import Auth


def find_by_id(auth_id=4):
    return db.session.query(Auth).filter_by(id=auth_id).first()


def find_by_name(auth_name="Student"):
    return db.session.query(Auth).filter_by(name=auth_name).first()
