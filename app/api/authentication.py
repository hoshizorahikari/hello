from flask import g, jsonify
from flask_httpauth import HTTPBasicAuth

from . import api
from ..models import AnonymousUser, User
from .errors import forbidden, unauthorized

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(email_or_token, password):
    # 验证回调函数
    if email_or_token == '':  # 匿名用户访问
        #g.current_user = AnonymousUser()
        return False#True
    # 密码为空,则提供的是令牌
    if password == '':
        g.current_user = User.verify_auth_token(email_or_token)
        g.token_used = True
        return g.current_user is not None
    # 使用邮箱和密码验证
    user = User.query.filter_by(email=email_or_token).first()
    if not user:  # 用户不存在
        return False
    # 通过认证的用户保存在全局对象g中,视图函数能访问
    g.current_user = user
    g.token_used = False
    # 使用User模型的验证方法验证用户密码
    return user.verify_password(password)


@auth.error_handler
def auth_error():
    return unauthorized('Invalid credentials')


@api.before_request
@auth.login_required
def before_request():
    # 不是匿名用户(已经认证)但是没有激活账号,抛出403
    if not g.current_user.is_anonymous and \
            not g.current_user.confirmed:
        return forbidden('Unconfirmed account')


@api.route('/tokens/', methods=['POST'])
def get_token():
    # 如匿名用户或已经有令牌,需要拒绝请求
    if g.current_user.is_anonymous or g.token_used:
        return unauthorized('Invalid credentials')
    # 登录用户且没有生成令牌的用户返回JSON响应
    return jsonify({'token': g.current_user.gen_auth_token(
        expiration=3600), 'expiration': 3600})
