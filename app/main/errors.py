from flask import render_template
from . import main

# 如果使用errorhandler装饰器, 只能处理蓝本中的错误;
# 使用app_errorhandler装饰器, 注册全局错误处理


@main.app_errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@main.app_errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


@main.app_errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

