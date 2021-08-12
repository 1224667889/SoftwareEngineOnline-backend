from models.pairs import Pair
from app import db


def find_by_id(pair_id):
    return db.session.query(Pair).\
        filter_by(id=pair_id).first()


def find_by_code(code):
    return db.session.query(Pair).\
        filter_by(code=code).first()


def find_by_name(name):
    return db.session.query(Pair).\
        filter_by(name=name).first()
