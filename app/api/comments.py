from flask import jsonify, request, g, url_for, current_app
from .. import db
from ..models import Blog, Permission, Comment
from . import api
from .decorators import permission_required


@api.route('/comments/')
def get_comments():  # 1.所有评论的分页
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_comments', page=page-1)
    if pagination.has_next:
        next = url_for('api.get_comments', page=page+1)
    return jsonify({
        'comments': [c.to_json() for c in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/comments/<int:id>')
def get_comment(id):  # 2.获取某条评论
    c = Comment.query.get_or_404(id)
    return jsonify(c.to_json())


@api.route('/blogs/<int:id>/comments/')
def get_blog_comments(id):  # 3.某篇文章所有评论的分页
    b = Blog.query.get_or_404(id)
    page = request.args.get('page', 1, type=int)
    pagination = b.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    prev, next = None, None
    if pagination.has_prev:
        prev = url_for('api.get_blog_comments', id=id, page=page-1)
    if pagination.has_next:
        next = url_for('api.get_blog_comments', id=id, page=page+1)
    return jsonify({
        'comments': [c.to_json() for c in comments],
        'prev': prev,
        'next': next,
        'count': pagination.total
    })


@api.route('/blogs/<int:id>/comments/', methods=['POST'])
@permission_required(Permission.COMMENT)
def new_blog_comment(id):  # 4.创建新评论
    b = Blog.query.get_or_404(id)
    c = Comment.from_json(request.json)
    c.author = g.current_user
    c.blog = b
    db.session.add(c)
    db.session.commit()
    return jsonify(c.to_json()), 201, \
        {'Location': url_for('api.get_comment', id=c.id)}
