from models.users import User
from . import test
from flask import request
from servers import notices
from utils.middleware import login_required
from utils import serialization
from app import mongo


@test.route("/hello")
def test_hello():
    # 增
    mongo.db.uploads.insert({
        "id": 1,
        "ip": "127.0.0.1",
        "user_id": 1,
    })
    # 删
    m = mongo.db.uploads.find_one({'id': 1})
    mongo.db.uploads.remove(m)
    # 改
    m = mongo.db.uploads.find_one({'id': 1})
    m['ip'] = '255.255.255.255'
    mongo.db.uploads.save(m)
    # 查
    page_size = 10
    page_number = 1
    skip = page_size * (page_number - 1)
    total_uploads = mongo.db.uploads.find({'id': 1})
    total = 0
    for _ in total_uploads:
        total += 1
    total_page = total // page_size
    if total % page_size != 0:
        total_page += 1
    uploads = mongo.db.uploads.find({'id': 1}).limit(page_size).skip(skip)
    return {"uploads": [upload.items() for upload in uploads]}
