import os

from flask import Flask, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap

from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# from flask_moment import Moment
# from datetime import datetime

# flask程序根目录
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
# 配置sqlite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')  # 配置sqlite的URL,数据库名字data.sqlite
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 自动提交修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
app.config['SECRET_KEY'] = 'hoshizora rin'  # csrf保护


bootstrap = Bootstrap(app)
# moment = Moment(app)

manager = Manager(app)

from flask_mail import Mail
# -------------
app.config['MAIL_SERVER'] = 'smtp.163.com'
app.config['MAIL_PORT'] = 25#465  # SMTP的加密SSL端口
# app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')  # xxx@163.com
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')  # 授权码, 不是密码
mail = Mail(app)
# -----------------

from flask_mail import Message
app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
app.config['FLASKY_MAIL_SENDER'] = 'Flasky Admin <flasky@example.com>'
def send_email(to, subject, template, **kwargs):
    # to为接收方,subject为邮件主题,template为渲染邮件正文的模板
    msg = Message(app.config['FLASKY_MAIL_SUBJECT_PREFIX'] + ' ' + subject,
                  sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    mail.send(msg)

#--------
app.config['FLASKY_ADMIN'] = os.environ.get('FLASKY_ADMIN')



class NameForm(FlaskForm):  # 一个文本字段和一个提交按钮
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('提交')

# -------------------------


class Role(db.Model):
    __tablename__ = 'roles'  # 表名
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name


class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    username = db.Column(db.String(64), unique=True, index=True)
    role_id = db.Column(db.Integer, db.ForeignKey(
        'roles.id'))  # 外键, roles表中的id

    def __repr__(self):
        return '<User %r>' % self.username


# ----------------
@app.route('/', methods=['GET', 'POST'])  # 支持GET和POST
def index():
    form = NameForm()
    if form.validate_on_submit():  # 提交表单,数据被验证函数接受
        user = User.query.filter_by(username=form.name.data).first()  # 数据库查询
        if user is None:  # 数据库不存在用户则添加
            user = User(username=form.name.data)
            db.session.add(user)
            session['known'] = False
            if app.config['FLASKY_ADMIN']:
                print(app.config['FLASKY_ADMIN'])
                send_email(app.config['FLASKY_ADMIN'], 'New User', 'mail/new_user', user=user)

        else:
            session['known'] = True
        session['name'] = form.name.data  # 获取字段data属性存入session
        form.name.data = ''  # 清空文本框
        return redirect(url_for('index'))  # 重定向, GET方式请求index
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))


# @app.route('/')
# def index():
#     return render_template('index.html', now=datetime.utcnow())


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


# ----------------
# 注册了应用app、数据库实例db、模型User和Role


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
# -----------------
# 配置Flask-Migrate
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # 默认端口5000, 可以修改
    # app.run(debug=True, port=8000)
    manager.run()
