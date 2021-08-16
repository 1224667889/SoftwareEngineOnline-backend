"""结对功能"""
from . import user
from flask import request
from models.users import User
from models.pairs import Pair
from servers import pairs, users
from utils.middleware import login_required
from utils import serialization
from utils.logger import logger


# 获取队伍详情
@user.route('/pair', methods=['GET'])
@login_required("Student")
def get_pair(login_user: User):
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    return serialization.make_resp(login_user.pair.get_msg(), code=200)

# 创建队伍
@user.route('/pair', methods=['POST'])
@login_required("Student")
def create_pair(login_user: User):
    name = request.form.get("name")
    if not name:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    if pairs.find_by_name(name):
        return serialization.make_resp({"error_msg": "队名重复"}, code=40003)
    p = Pair()
    e = p.add(login_user, name, commit=True)
    if e:
        if e == 1:
            return serialization.make_resp({"error_msg": "已有队伍"}, code=40001)
        return serialization.make_resp({"error_msg": "队伍创建失败，换个名称再试试"}, code=500)
    return serialization.make_resp(p.get_msg(), code=200)

# 加入队伍
@user.route('/pair/<string:code>', methods=['GET'])
@login_required("Student")
def join_pair(login_user: User, code):
    p = pairs.find_by_code(code)
    if not p:
        return serialization.make_resp({"error_msg": "邀请码错误"}, code=404)
    e = p.join(login_user, commit=True)
    if e:
        if e == 1:
            return serialization.make_resp({"error_msg": "已有队伍"}, code=40001)
        if e == 2:
            return serialization.make_resp({"error_msg": "队伍已满"}, code=40002)
        return serialization.make_resp({"error_msg": "队伍加入失败"}, code=500)
    return serialization.make_resp(p.get_msg(), code=200)

# 编辑队伍
@user.route('/pair', methods=['PUT'])
@login_required("Student")
def put_pair(login_user: User):
    # 队长编辑
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    if login_user.pair.captain_id != login_user.id:
        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
    try:
        proportions = list(request.json.get("proportions"))
    except Exception as e:
        logger.error(e)
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    e = login_user.pair.set_proportions(proportions)
    if e:
        if e == 1:
            return serialization.make_resp({"error_msg": "学号不匹配"}, code=400)
        return serialization.make_resp({"error_msg": "修改失败，请检测参数"}, code=500)
    return serialization.make_resp(login_user.pair.get_msg(), code=200)

# 编辑队伍名称
@user.route('/pair/name', methods=['PUT'])
@login_required("Student")
def put_name_pair(login_user: User):
    # 队长编辑
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    if login_user.pair.captain_id != login_user.id:
        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
    name = request.form.get("name")
    if not name:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    if login_user.pair.set_name(name):
        return serialization.make_resp({"error_msg": "名称修改失败，换个名称再试试"}, code=500)
    return serialization.make_resp(login_user.pair.get_msg(), code=200)

# 离开队伍
@user.route('/pair/me', methods=['DELETE'])
@login_required("Student")
def leave_pair(login_user: User):
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    if login_user.pair.captain_id == login_user.id:
        return serialization.make_resp({"error_msg": "你是队长，请先转让队长职位，或直接解散队伍"}, code=401)
    password = request.form.get("password")
    if not password:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    if not login_user.verify_password(password):
        return serialization.make_resp({"error_msg": "密码错误"}, code=400)
    if login_user.leave_pair():
        return serialization.make_resp({"error_msg": "修改失败，请联系管理员"}, code=500)
    return serialization.make_resp({"msg": "退出成功"}, code=200)

# 解散队伍
@user.route('/pair', methods=['DELETE'])
@login_required("Student")
def delete_pair(login_user: User):
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    if login_user.pair.captain_id != login_user.id:
        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
    password = request.form.get("password")
    if not password:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    if not login_user.verify_password(password):
        return serialization.make_resp({"error_msg": "密码错误"}, code=400)
    if login_user.pair.delete():
        return serialization.make_resp({"error_msg": "修改失败，请联系管理员"}, code=500)
    return serialization.make_resp({"msg": "解散成功"}, code=200)

# 移交队长
@user.route('/pair/<string:student_id>', methods=['PUT'])
@login_required("Student")
def change_owner_pair(login_user: User, student_id):
    if not login_user.pair:
        return serialization.make_resp({"error_msg": "未加入队伍"}, code=40004)
    if login_user.pair.captain_id != login_user.id:
        return serialization.make_resp({"error_msg": "权限不足"}, code=401)
    password = request.form.get("password")
    if not password:
        return serialization.make_resp({"error_msg": "参数错误"}, code=400)
    if not login_user.verify_password(password):
        return serialization.make_resp({"error_msg": "密码错误"}, code=400)
    e = login_user.pair.set_captain(users.find_by_student_id(student_id))
    if e:
        if e == 1:
            return serialization.make_resp({"error_msg": "修改失败，队伍内无此人"}, code=404)
        if e == 2:
            return serialization.make_resp({"error_msg": "不能移交给自己"}, code=400)
        return serialization.make_resp({"error_msg": "修改失败，请联系管理员"}, code=500)
    return serialization.make_resp({"msg": "修改成功"}, code=200)
