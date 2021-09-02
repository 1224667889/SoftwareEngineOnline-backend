"""JWT"""
from flask import request
import functools

from servers import users
from utils import serialization
from config import SECRET_KEY, spider_token
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import BadSignature, SignatureExpired


def login_required(*auths_need):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kw):
            try:
                '''在请求头上拿到token'''
                token = request.headers["Authorization"]
            except Exception as e:
                '''没接收的到token,给前端抛出错误'''
                return serialization.make_resp({"error_msg": "token缺失"}, code=400)
            try:
                token = token.split()[-1]
                s = Serializer(SECRET_KEY)
                user_id = s.loads(token)["id"]
                user = users.find_by_id(user_id)
                if not user:
                    """用户不存在"""
                    return serialization.make_resp({"error_msg": "用户不存在"}, code=404)
                if auths_need:
                    '''获取token中的权限列表如果在参数列表中则表示有权限，否则就表示没有权限'''
                    if not [auth.name for auth in user.auths if auth.name in auths_need]:
                        # 交集为空,表示权限不足
                        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
            except SignatureExpired:
                '''token正确但是过期了'''
                return serialization.make_resp({"error_msg": "token过期"}, code=50001)
            except BadSignature:
                '''token错误'''
                return serialization.make_resp({"error_msg": "token错误"}, code=50000)
            except Exception:
                return serialization.make_resp({"error_msg": "token错误"}, code=50000)
            return func(user, *args, **kw)
        return wrapper
    return decorator


def spider_jwt(func):
    @functools.wraps(func)
    def wrapper(*args, **kwags):
        token = request.headers["Authorization"].split()[-1]
        if token != spider_token:
            return {
                "code": 401,
                "msg": "权限不足"
            }
        return func(*args, **kwags)
    return wrapper


def generate_token(user, expiration=864000):
    # 默认十天过期
    s = Serializer(SECRET_KEY, expires_in=expiration)   # expiration是过期时间3600:一小时
    token = s.dumps({'id': user.id}).decode('utf-8')
    return token
