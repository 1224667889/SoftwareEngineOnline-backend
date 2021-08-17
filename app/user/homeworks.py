"""作业功能"""
from . import user
from flask import request, Response
from models.users import User
from servers import homeworks
from utils.middleware import login_required
from utils import serialization
from utils.logger import logger
from config import documents_path

# 下载文档
@user.route("/homework/document/<string:u_name>", methods=['GET'])
@login_required("SuperAdmin", "Admin", "Student")
def document_upload(login_user: User, u_name):
    document = homeworks.find_document_u_name(u_name)
    if not document:
        return serialization.make_resp({"error_msg": "文档不存在"}, code=404)
    try:
        # 流式文件
        def send_file():
            store_path = documents_path + document.u_name
            with open(store_path, 'rb') as f:
                while 1:
                    data = f.read(1 * 1024 * 1024)  # 每次读取1MB (可用限速)
                    if not data:
                        break
                    yield data
        response = Response(send_file(), content_type='application/octet-stream')
        response.headers["Content-disposition"] = 'attachment; filename=%s' % \
                                                  document.name.encode("utf-8").decode("latin1")
        return response
    except Exception as e:
        logger.error(e)
        return serialization.make_resp({"error_msg": "文档返回失败"}, code=500)
