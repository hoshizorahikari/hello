from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required  # , current_user
from . import auth
from ..models import User
from .forms import LoginForm, RegistrationForm
from .. import db
from ..email import send_mail


@auth.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        # 根据输入邮箱查询用户
        user = User.query.filter_by(email=form.email.data).first()
        # 如果用户存在且密码正确
        if user and user.verify_password(form.password.data):
            login_user(user, form.remember_me.data)
            nxt = request.args.get('next')
            # 没有next重定向到首页
            if nxt is None or not nxt.startswith('/'):
                nxt = url_for('main.index')
            return redirect(nxt)
        flash('用户名或密码错误！')  # 认证失败
    return render_template('auth/login.html', form=form)


@auth.route('/logout')
@login_required
def logout():  # 登出用户
    logout_user()  # 删除并重设用户会话
    flash('你已经退出...')  # 显示登出消息
    return redirect(url_for('main.index'))  # 重定向至首页


@auth.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data,
                    username=form.username.data, password=form.password.data)
        db.session.add(user)
        # 即使自动提交,此处也要commit,因为要获取id用于生成确认令牌,不能延后提交
        db.session.commit()
        token = user.generate_confirmation_token()
        send_mail(user.email, 'Confirm Your Account',
                  'auth/email/confirm', user=user, token=token)
        flash('A confirmation email has been sent to you by email.')
        # flash('注册成功！现在可以登录了！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', form=form)
