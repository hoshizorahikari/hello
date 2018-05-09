from functools import wraps
from flask import abort
from flask_login import current_user
from .models import Permission


def permission_required(p):  # 需要权限p的装饰器
    # 带参数的装饰器, 需要三层嵌套
    def decorator(f):
        # 使用装饰器后,f指向内层函数wrap,__name__变为wrap
        # @wraps(f)使得f获得原来__name__等属性
        @wraps(f)
        def wrap(*args, **kwargs):
            if not current_user.can(p):
                abort(403)  # 没权限p返回403错误码
            return f(*args, **kwargs)
        return wrap
    return decorator


def admin_required(f):  # 需要管理员权限的装饰器
    return permission_required(Permission.ADMIN)(f)
