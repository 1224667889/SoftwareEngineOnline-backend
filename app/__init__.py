"""生成flask_app"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from config import dbConfig, SECRET_KEY
import pymongo


db = SQLAlchemy()
mongoCli = pymongo.MongoClient('mongodb://localhost:27017/')  # 开启数据库实例


def create_app(debug=False):
    app = Flask(__name__)
    app.debug = debug
    app.config['SECRET_KEY'] = SECRET_KEY
    # 链接mysql
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://%s:%s@%s:%d/%s' \
                                            % (dbConfig['user'],
                                               dbConfig['password'],
                                               dbConfig['host'],
                                               dbConfig['port'],
                                               dbConfig['database'])
    # 链接mongoDB
    # app.config['MONGO_URI'] = 'mongodb://localhost:27017/'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    app.url_map.strict_slashes = False

    db.init_app(app)
    # mongo.init_app(app)

    from .user import user as user_blueprint
    from .admin import admin as admin_blueprint
    from .test import test as test_blueprint
    app.register_blueprint(user_blueprint, url_prefix='/api/user/')
    app.register_blueprint(admin_blueprint, url_prefix='/api/admin/')
    app.register_blueprint(test_blueprint, url_prefix='/api/test/')
    return app
