from flask import render_template, request, jsonify
from . import main

# 如果使用errorhandler装饰器, 只能处理蓝本中的错误;
# 使用app_errorhandler装饰器, 注册全局错误处理


@main.app_errorhandler(403)
def forbidden(e):
    # 检查Accept请求首部,决定客户端期望接收的响应格式
    # 为只接受JSON格式不接受HTML格式的客户端生成JSON格式响应
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'forbidden'})
        response.status_code = 403
        return response
    # 浏览器一般不限制响应格式, 返回HTML格式响应
    return render_template('403.html'), 403


@main.app_errorhandler(404)
def page_not_found(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'not found'})
        response.status_code = 404
        return response
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    if request.accept_mimetypes.accept_json and \
            not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'internal server error'})
        response.status_code = 500
        return response
    return render_template('500.html'), 500
