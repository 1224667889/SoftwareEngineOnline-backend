"""JWT"""
from flask import request, jsonify
import functools


def login_required(*role):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                '''在请求头上拿到token'''
                token = request.headers["Authorization"]
            except Exception as e:
                '''没接收的到token,给前端抛出错误'''
                return jsonify({"status": 400, "msg": "缺少参数token"})
            token = token.split()[-1]
            try:
                if role:
                    '''获取token中的权限列表如果在参数列表中则表示有权限，否则就表示没有权限'''
                    rights = []     # Todo: 权限组鉴权or身份鉴权
                    if not [r for r in rights if r in role]:
                        # 交集为空
                        return jsonify({"status": 400, "msg": "权限不足"})
            except Exception as e:
                '''token错误'''
                return jsonify({"status": 400, "msg": e})
            return func(*args, **kw)
        return wrapper
    return decorator
