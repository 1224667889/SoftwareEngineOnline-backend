"""权限"""
from app import db

users_auths = db.Table('users_auths',
                       db.Column('user_id',
                                 db.Integer,
                                 db.ForeignKey('users.id')
                                 ),
                       db.Column('auth_id',
                                 db.Integer,
                                 db.ForeignKey('auths.id')
                                 )
                       )


class Auth(db.Model):
    __tablename__ = 'auths'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), unique=True)
    description = db.Column(db.String(255))


