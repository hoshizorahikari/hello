from flask import render_template, abort, flash, url_for, redirect, request, current_app
from ..models import User, Role, Permission, Blog
from . import main
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm, BlogForm
from .. import db
from ..decorators import admin_required,permission_required


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
    # 分页
    # 查询字符串(request.args)获取页数,默认第1页;type=int保证参数无法转为int时返回默认值
    page = request.args.get('page', 1, type=int)
    # page为第几页;per_page为每页几个记录,默认20;
    # error_out默认为True,表示页数超过范围404错误,False则返回空列表
    pagination = Blog.query.order_by(Blog.timestamp.desc()).paginate(
        page, per_page=current_app.config['BLOGS_PER_PAGE'], error_out=False)
    blogs = pagination.items

    # 按时间戳降序, 最近的靠前
    # blogs = Blog.query.order_by(Blog.timestamp.desc()).all()
    return render_template('index.html', form=form, blogs=blogs,
                           pagination=pagination)


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

@main.route('/blog/<int:id>')
def blog(id):
    b = Blog.query.get_or_404(id)
    return render_template('blog.html', blogs=[b])

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
    if user is None:
        flash('无效用户！')
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
    if user is None:
        flash('无效用户！')
        return redirect(url_for('.index'))
    if not current_user.is_following(user):
        flash('你没有关注此用户，无法取消关注！')
        return redirect(url_for('.user', username=username))
    current_user.unfollow(user)
    flash('你取消关注了{}！'.format(username))
    return redirect(url_for('.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    # 关注此用户的小弟们
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('无效用户！')
        return redirect(url_for('.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(
        page, per_page=current_app.config['FOLLOWERS_PER_PAGE'],
        error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp}
               for item in pagination.items]
    return render_template('followers.html', user=user, title="Followers of",
                           endpoint='.followers', pagination=pagination,
                           follows=follows)


@main.route('/followed_by/<username>')
def followed_by(username):
    # 此用户关注大神们
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
    return render_template('followers.html', user=user, title="Followed by",
                           endpoint='.followed_by', pagination=pagination,
                           follows=follows)
