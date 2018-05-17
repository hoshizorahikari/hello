from flask import g, jsonify, request, url_for, current_app

from . import api
from .. import db
from ..models import Blog, Permission
from .authentication import auth
from .decorators import permission_required
from .errors import forbidden


@api.route('/blogs/')
@auth.login_required
def get_blogs():
    # 获取所有博客文章,JSON响应是这个集合的一部分
    page = request.args.get('page', 1, type=int)
    pagination = Blog.query.paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'],
        error_out=False)
    blogs = pagination.items
    # prev和next字段表示上一页和下一页资源的URL
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_blogs', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_blogs', page=page+1)

    return jsonify({
        'blogs': [b.to_json() for b in blogs],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/blogs/<int:id>')
@auth.login_required
def get_blog(id):
    # 获取指定id的文章
    b = Blog.query.get_or_404(id)
    return jsonify(b.to_json())


@api.route('/blogs/', methods=['POST'])
@permission_required(Permission.WRITE)  # 当前登录用户需要写文章的权限
def new_blog():
    # 从请求获取JSON数据,创建Blog对象
    b = Blog.from_json(request.json)
    b.author = g.current_user  # 作者为当前登录用户
    db.session.add(b)
    db.session.commit()
    return jsonify(b.to_json()), 201,\
        {'Location': url_for('api.get_blog', id=b.id)}


@api.route('/blogs/<int:id>', methods=['PUT'])
@permission_required(Permission.WRITE)
def edit_blog(id):
    b = Blog.query.get_or_404(id)
    # 非作者和非管理员不能修改
    if g.current_user != b.author and \
            not g.currrent_user.can(Permission.ADMIN):
        return forbidden('Insufficient permissions')
    # 如果没有body值,用原来的
    b.body = request.json.get('body', b.body)
    db.session.add(b)
    db.session.commit()
    return jsonify(b.to_json())
