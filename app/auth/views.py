from flask import render_template, redirect, request, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user
from . import auth
from ..models import User
from .forms import *
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


@auth.route('/confirm/<token>')
@login_required
def confirm(token):
    if current_user.confirmed:
        return redirect(url_for('main.index'))
    if current_user.confirm(token):
        # db.session.commit()
        flash('你已经账号已通过认证！')
    else:
        flash('认证链接无效或已经过期！')
    return redirect(url_for('main.index'))


@auth.before_app_request
def before_request():
    # 用户已登录,未确认,请求端点不在蓝本,请求被拦截,重定向至/unconfirmed
    if current_user.is_authenticated \
            and not current_user.confirmed \
            and request.endpoint \
            and request.blueprint != 'auth' \
            and request.endpoint != 'static':
        return redirect(url_for('auth.unconfirmed'))


@auth.route('/unconfirmed')
def unconfirmed():
    # 匿名或已经确认,没必要确认,重定向至首页
    if current_user.is_anonymous or current_user.confirmed:
        return redirect(url_for('main.index'))
    # 显示一个确认账户相关信息的页面
    return render_template('auth/unconfirmed.html')


@auth.route('/confirm')
@login_required
def resend_confirmation():
    # 重新发送确认邮件,需要用户已登录
    token = current_user.generate_confirmation_token()
    send_mail(current_user.email, 'Confirm Your Account',
              'auth/email/confirm', user=current_user, token=token)
    flash('A new confirmation email has been sent to you by email.')
    return redirect(url_for('main.index'))


@auth.route('/change_password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        # 原密码输入正确,设置新密码
        if current_user.verify_password(form.old_password.data):
            current_user.password = form.password.data
            db.session.add(current_user)
            # db.session.commit()
            flash('密码修改成功！')
            return redirect(url_for('main.index'))
        else:
            flash('原密码输入有误！')
    return render_template('auth/change_password.html', form=form)


@auth.route('/reset', methods=['GET', 'POST'])
def password_reset_request():
    # 匿名用户什么也不做,重定向到首页
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:  # 生成重置令牌,发送邮件
            token = user.generate_reset_token()
            send_mail(user.email, 'Reset Your Password', 'auth/email/reset_password',
                      user=user, token=token, next=request.args.get('next'))
        flash('An email with instructions to reset your password has been sent to you.')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/reset/<token>', methods=['GET', 'POST'])
def password_reset(token):
    if not current_user.is_anonymous:
        return redirect(url_for('main.index'))
    form = PasswordResetForm()
    if form.validate_on_submit():
        if User.reset_password(token, form.password.data):
            # db.session.commit()
            flash('重设密码成功！')
            return redirect(url_for('auth.login'))
        else:
            return redirect(url_for('main.index'))
    return render_template('auth/reset_password.html', form=form)


@auth.route('/change_email', methods=['GET', 'POST'])
@login_required
def change_email_request():
    form = ChangeEmailForm()
    if form.validate_on_submit():
        if current_user.verify_password(form.password.data):
            new_email = form.email.data
            token = current_user.generate_email_change_token(new_email)
            send_mail(new_email, 'Confirm your email address',
                      'auth/email/change_email',
                      user=current_user, token=token)
            flash(
                'An email with instructions to confirm your new email address has been sent to you.')
            return redirect(url_for('main.index'))
        else:
            flash('邮箱或密码有误！')
    return render_template("auth/change_email.html", form=form)


@auth.route('/change_email/<token>')
@login_required
def change_email(token):
    if current_user.change_email(token):
        # db.session.commit()
        flash('修改邮箱成功！')
    else:
        flash('无效请求！')
    return redirect(url_for('main.index'))
