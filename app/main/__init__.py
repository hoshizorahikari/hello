from flask import Blueprint
# 创建蓝本对象, 参数为蓝本的名字和蓝本所在包或模块
main = Blueprint('main', __name__)
# app/main/view.py保存路由和视图函数; app/main/errors.py保存错误处理
# 导入这两个模块是为了将路由和错误处理与蓝本关联起来
# 末尾导入为了避免循环导入, 因为views.py和errors.py要导入蓝本main
from . import views, errors
