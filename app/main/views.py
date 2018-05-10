from flask import render_template, abort, flash, url_for, redirect
from ..models import User, Role
from . import main
from flask_login import login_required, current_user
from .forms import EditProfileForm, EditProfileAdminForm
from .. import db
from ..decorators import admin_required


@main.route('/')
def index():
    return render_template('index.html')


@main.route('/user/<username>')
def user(username):
    # 根据用户名查询用户对象,没有返回404
    user = User.query.filter_by(username=username).first_or_404()
    return render_template('user.html', user=user)


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


