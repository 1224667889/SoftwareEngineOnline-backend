from models.teams import Team
from app import db


def find_by_id(team_id):
    return db.session.query(Team).\
        filter_by(id=team_id).first()


def find_by_code(code):
    return db.session.query(Team).\
        filter_by(code=code).first()


def find_by_name(name):
    return db.session.query(Team).\
        filter_by(name=name).first()
