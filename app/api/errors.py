from flask import jsonify
from . import api
from ..exceptions import ValidationError


def bad_request(message):
    response = jsonify({'error': 'bad request', 'message': message})
    response.status_code = 400
    return response


def unauthorized(message):
    response = jsonify({'error': 'unauthorized', 'message': message})
    response.status_code = 401
    return response


def forbidden(message):
    response = jsonify({'error': 'forbidden', 'message': message})
    response.status_code = 403
    return response


@api.errorhandler(ValidationError)
# 只要抛出指定类异常,就会调用被装饰的函数
# api.errorhandler只有API蓝本的路由抛出异常才会调用
def validation_error(e):
    return bad_request(e.args[0])
