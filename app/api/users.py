from flask import jsonify, request, current_app, url_for
from . import api
from ..models import User, Blog


@api.route('/users/<int:id>')
def get_user(id):  # 1.某个用户
    user = User.query.get_or_404(id)
    return jsonify(user.to_json())


@api.route('/users/<int:id>/blogs/')
def get_user_blogs(id):  # 2.该用户所有文章的分页
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.blogs.order_by(Blog.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'],
        error_out=False)
    blogs = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_user_blogs', id=id, page=page-1)
    if pagination.has_next:
        next = url_for('api.get_user_blogs', id=id, page=page+1)
    return jsonify({
        'blogs': [b.to_json() for b in blogs],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/users/<int:id>/timeline/')
def get_user_followed_blogs(id):  # 3.该用户关注的大神的所有文章的分页
    user = User.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = user.followed_blogs.order_by(Blog.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'],
        error_out=False)
    blogs = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_user_followed_blogs', id=id, page=page-1)
    if pagination.has_next:
        next = url_for('api.get_user_followed_blogs', id=id, page=page+1)
    return jsonify({
        'blogs': [b.to_json() for b in blogs],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })
