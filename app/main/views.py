from flask import render_template, abort, flash, url_for, redirect, request, current_app
from ..models import User, Role, Permission, Blog, Comment
from . import main
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, BlogForm, CommentForm
from .. import db
from ..decorators import admin_required, permission_required


@main.route('/', methods=['GET', 'POST'])
def index():
    form = BlogForm()
    # 是否有写博客的权限
    if current_user.can(Permission.WRITE) and form.validate_on_submit():
        blog = Blog(body=form.body.data,
                    author=current_user._get_current_object())
        db.session.add(blog)
        # db.session.commit()
        return redirect(url_for('.index'))
        # return redirect(url_for('.blog',id=blog.id))
    # 分页
    # 查询字符串(request.args)获取页数,默认第1页;type=int保证参数无法转为int时返回默认值
    page = request.args.get('page', 1, type=int)

    # show_followed存储在cookie中, 是否只显示关注用户文章
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    query = current_user.followed_blogs if show_followed else Blog.query.filter_by(disabled=False)

    # page为第几页;per_page为每页几个记录,默认20;
    # error_out默认为True,表示页数超过范围404错误,False则返回空列表
    pagination = query.order_by(Blog.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items

    # 按时间戳降序, 最近的靠前
    # blogs = Blog.query.order_by(Blog.timestamp.desc()).all()
    return render_template('index.html', form=form, blogs=blogs,
                           show_followed=show_followed, pagination=pagination)


@main.route('/user/<username>')
def user(username):
    # 根据用户名查询用户对象,没有返回404
    user = User.query.filter_by(username=username).first_or_404()
    # 查询该用户的文章列表, 按时间戳降序
    page = request.args.get('page', 1, type=int)
    # page为第几页;per_page为每页几个记录,默认20;
    # error_out默认为True,表示页数超过范围404错误,False则返回空列表
    pagination = user.blogs.order_by(Blog.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE']//2+1, error_out=False)
    blogs = pagination.items
    # blogs = user.blogs.order_by(Blog.timestamp.desc()).all()
    return render_template('user.html', user=user, blogs=blogs,
                           pagination=pagination)


@main.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        # post请求,获取表单数据,提交到数据库
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user._get_current_object())
        # db.session.commit()
        flash('修改成功！')
        return redirect(url_for('.user', username=current_user.username))
    # get请求使用数据库数据渲染表单,让用户修改
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/edit_profile/<int:id>', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_profile_admin(id):
    # 管理员资料编辑视图整体结构和普通用户类似,只不过参数略多
    # 根据id获取用户对象
    user = User.query.get_or_404(id)
    form = EditProfileAdminForm(user=user)
    if form.validate_on_submit():
        user.email = form.email.data.lower()
        user.username = form.username.data.lower()
        user.confirmed = form.confirmed.data
        # select下拉菜单得到的role_id是int,以此来查询对应Role对象
        user.role = Role.query.get(form.role.data)
        user.name = form.name.data
        user.location = form.location.data
        user.about_me = form.about_me.data
        user.image = form.image.data
        db.session.add(user)
        # db.session.commit()
        flash('修改成功！')
        return redirect(url_for('.user', username=user.username))
    form.email.data = user.email
    form.username.data = user.username
    form.confirmed.data = user.confirmed
    form.role.data = user.role_id
    form.name.data = user.name
    form.location.data = user.location
    form.about_me.data = user.about_me
    form.image.data = user.image
    # 管理员资料编辑和普通用户使用同一个模板
    return render_template('edit_profile.html', form=form, user=user)


# @main.route('/blog/<int:id>')
# def blog(id):
#     b = Blog.query.get_or_404(id)
#     return render_template('blog.html', blogs=[b])


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    b = Blog.query.get_or_404(id)
    # 当前登录用户是文章的作者或管理员可以编辑
    if current_user != b.author and \
            not current_user.can(Permission.ADMIN):
        abort(403)
    form = BlogForm()
    if form.validate_on_submit():
        b.body = form.body.data
        db.session.add(b)
        # db.session.commit()
        flash('修改成功！')
        return redirect(url_for('.blog', id=b.id))
    form.body.data = b.body
    return render_template('edit_blog.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    # 关注该资料页用户
    user = User.query.filter_by(username=username).first()
    if user is None or current_user == user:
        flash('无效操作！')
        return redirect(url_for('.index'))
    if current_user.is_following(user):
        flash('你已经关注了此用户！')
        return redirect(url_for('.user', username=username))
    current_user.follow(user)
    flash('你成功关注了{}。'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    # 取消关注
    user = User.query.filter_by(username=username).first()
    if user is None or current_user == user:
        flash('无效操作！')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你没有关注此用户，无法取消关注！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('你取消关注了{}！'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    # 显示关注此用户的小弟们
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        # 在配制文件设置一页显示多少关注者, 此处为50
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    # 关注者、关注时间字典组成的列表
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    title = '关注{}的人'.format(username)
    return render_template('followers.html', user=user, title=title,
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    # 显示此用户关注的大神们
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp}
               for item in pagination.items]
    title = '{}关注的人'.format(username)
    return render_template('followers.html', user=user, title=title,
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)


from flask import make_response


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '', max_age=30*24*60*60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('.index')))
    resp.set_cookie('show_followed', '1', max_age=30*24*60*60)
    return resp


@main.route('/blog/<int:id>', methods=['GET', 'POST'])
def blog(id):  # 单个博客文章页面
    b = Blog.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        c = Comment(body=form.body.data,
                    blog=b,
                    author=current_user._get_current_object())
        db.session.add(c)
        # db.session.commit()
        flash('评论成功！')
        return redirect(url_for('.blog', id=b.id, page=-1))
    page = request.args.get('page', 1, type=int)
    n = current_app.config['COMMENTS_PER_PAGE']  # 配置文件设为30
    if page == -1:  # 评论最后一页;因为先评论的在前,刚提交的评论在最后
        page = (b.comments.count()-1)//n+1
    pagination = b.comments.order_by(Comment.timestamp.asc()).paginate(
        page, per_page=n, error_out=False)
    comments = pagination.items
    return render_template('blog.html', blogs=[b], form=form,
                           comments=comments, pagination=pagination)


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE)
def moderate():
    # 从数据库读取一页评论
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(Comment.timestamp.desc()).paginate(
        page, per_page=current_app.config['COMMENTS_PER_PAGE'],
        error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_enable(id):
    c = Comment.query.get_or_404(id)
    c.disabled = False
    db.session.add(c)
    # db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def moderate_disable(id):
    c = Comment.query.get_or_404(id)
    c.disabled = True
    db.session.add(c)
    # db.session.commit()
    return redirect(url_for('.moderate',
                            page=request.args.get('page', 1, type=int)))


@main.route('/shutdown')
def server_shutdown():
    # 非测试环境不能用,直接404
    if not current_app.testing:
        abort(404)
    # 获取Werkzeug在环境中提供的关闭函数
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:  # 没有获取到函数,500错误
        abort(500)
    shutdown()  # 成功获取关闭函数,执行此函数
    print('ready to shutdown...')
    return 'Shutting down...'


from flask_sqlalchemy import get_debug_queries


@main.after_app_request
def after_request(response):

    for q in get_debug_queries():
        # 查询时间≥设定的阈值(此处为0.5s)的查询写入日志
        if q.duration >= current_app.config['SLOW_DB_QUERY_TIME']:
            """
            statement: SQL语句
            parameters: SQL语句参数
            start_time: 执行查询时的时间
            end_time: 返回查询结果时的时间
            duration: 查询持续时间,单位为秒
            context: 表示查询在代码中所处位置的字符串
            """
            current_app.logger.warning(
                'Slow query:{}\nParameters:{}\nDuration:{}s\nContext:{}\n'.format(
                    q.statement, q.parameters, q.duration, q.context))
    return response


@main.route('/users')
@login_required
@permission_required(Permission.MODERATE)
def manage_users():
    # 从数据库读取一页评论
    page = request.args.get('page', 1, type=int)
    pagination = User.query.order_by(User.member_since.desc()).paginate(
        page, per_page=current_app.config['USERS_PER_PAGE'],
        error_out=False)
    users = pagination.items
    return render_template('manage_users.html',users=users,
                           pagination=pagination, page=page)


@main.route('/user/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def user_enable(id):
    u = User.query.get_or_404(id)
    u.disabled = False
    db.session.add(u)
    for c in u.comments.all():
        c.disable=False
        db.session.add(c)
    for b in u.blogs.all():
        b.disabled=False
        db.session.commit()
    # db.session.commit()
    return redirect(url_for('.manage_users',
                            page=request.args.get('page', 1, type=int)))


@main.route('/user/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def user_disable(id):
    u = User.query.get_or_404(id)
    if u.can(Permission.MODERATE):
        flash('不能和谐管理员和协管员!')
    else:
        # 将该用户文章和评论全部和谐
        u.disabled = True
        db.session.add(u)
        for c in u.comments.all():
            c.disabled=True
            db.session.add(c)
        for b in u.blogs.all():
            b.disabled=True
            db.session.commit()
    # db.session.commit()
    return redirect(url_for('.manage_users',
                            page=request.args.get('page', 1, type=int)))

                    
# @main.route('/blog/enable/<int:id>')
# @login_required
# @permission_required(Permission.MODERATE)
# def blog_enable(id):
#     b = Blog.query.get_or_404(id)
#     b.disabled = False
#     db.session.add(b)

#     # db.session.commit()
#     return redirect(url_for('.index',
#                             page=request.args.get('page', 1, type=int)))


@main.route('/blog/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE)
def blog_disable(id):
    b = Blog.query.get_or_404(id)
    b.disabled = True
    db.session.add(b)
    # db.session.commit()
    return redirect(url_for('.index',
                            page=request.args.get('page', 1, type=int)))