from functools import wraps
from flask import g
from .errors import forbidden


def permission_required(p):
    def decorator(f):
        @wraps(f)
        def wrap(*args, **kwargs):
            if not g.current_user.can(p):
                # 没有权限p,返回权限不足
                return forbidden('Insufficient permissions')
            return f(*args, **kwargs)
        return wrap
    return decorator
