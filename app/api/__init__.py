from flask import Blueprint

api = Blueprint('api', __name__)  # 创建蓝本对象
# 导入模块将蓝本与它们关联起来
from . import authentication, blogs, users, comments, errors
