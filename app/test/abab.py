from models.users import User
from . import test
from flask import request
from servers import homeworks, users
from utils.middleware import login_required
from utils import serialization
from app import mongoCli


@test.route("/hello")
def test_hello():
    task = {
        "url": "blog.xx",				# 博客地址，留档、没用
        "html": "<body></body>",		# 文档原内容
        "git": "github.com/xx/ab",		# 项目地址
    }
    t = homeworks.find_by_id(4)
    err = t.save_mongo_doc(users.find_by_id(1), task)
    # return mongoCli["pair"].

    # mongoCli["pair"]["1"].insert({
    #     "id": 1,						# 可以是个人id，也可以是结对、团队id
    #     # "split": "标题1,标题2...",	# 分割标签，存于task->score->split表
    #     "task": {
    #         "url": "blog.xx",				# 博客地址，留档、没用
    #         "html": "<body></body>",		# 文档原内容
    #         "git": "github.com/xx/ab",		# 项目地址
    #     },
    #
    #     "scores": [						# 使用作业的评分细则生成评分
    #         {
    #             "point": "1.1",				    # 标签
    #             "description": "评分细则1",	    # 介绍
    #             "socre": 10,				    # 得分，不超过max
    #             "done": True				    # 是否已经评分
    #         },
    #         {
    #             "point": "1.2",				    # 标签
    #             "description": "评分细则2",	    # 介绍
    #             "socre": 0,					    # 得分，不超过max
    #             "done": False				    # 是否已经评分
    #         },
    #     ]
    # })
    return "1111"
    # # 增
    # mongo.db.uploads.insert({
    #     "id": 1,
    #     "ip": "127.0.0.1",
    #     "user_id": 1,
    # })
    # # 删
    # m = mongo.db.uploads.find_one({'id': 1})
    # mongo.db.uploads.remove(m)
    # # 改
    # m = mongo.db.uploads.find_one({'id': 1})
    # m['ip'] = '255.255.255.255'
    # mongo.db.uploads.save(m)
    # # 查
    # page_size = 10
    # page_number = 1
    # skip = page_size * (page_number - 1)
    # total_uploads = mongo.db.uploads.find({'id': 1})
    # total = 0
    # for _ in total_uploads:
    #     total += 1
    # total_page = total // page_size
    # if total % page_size != 0:
    #     total_page += 1
    # uploads = mongo.db.uploads.find({'id': 1}).limit(page_size).skip(skip)
    # return {"uploads": [upload.items() for upload in uploads]}
