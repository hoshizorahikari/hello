from flask import render_template, session, redirect, url_for, current_app
from .. import db
from ..models import User
from ..email import send_mail
from . import main
from .forms import NameForm


@main.route('/', methods=['GET', 'POST'])  # 支持GET和POST
def index():
    form = NameForm()
    if form.validate_on_submit():  # 提交表单,数据被验证函数接受
        user = User.query.filter_by(username=form.name.data).first()  # 数据库查询
        if user is None:  # 数据库不存在用户则添加
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            admin = current_app.config['FLASKY_ADMIN']
            if admin:
                send_mail(admin, 'New User', 'mail/new_user', user=user)
        else:
            session['known'] = True
        session['name'] = form.name.data  # 获取字段data属性存入session
        # 蓝本端点自动添加命名空间, 为main.index; 当前蓝本简写为.index
        return redirect(url_for('.index'))  # 重定向, GET方式请求index
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))
