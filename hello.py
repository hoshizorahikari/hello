import os
from flask import Flask, flash, redirect, render_template, session, url_for
from flask_bootstrap import Bootstrap
from flask_migrate import Migrate, MigrateCommand
from flask_script import Manager, Shell
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
from flask_moment import Moment
from datetime import datetime
from flask_mail import Mail, Message
from threading import Thread

# flask程序根目录
basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hoshizora rin'  # csrf保护
# 配置sqlite数据库
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + \
    os.path.join(basedir, 'data.sqlite')  # 配置sqlite的URL,数据库名字data.sqlite
app.config['SQLALCHEMY_COMMIT_ON_TEARDOWN'] = True  # 自动提交修改
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

app.config['MAIL_SERVER'] = 'smtp.qq.com'
app.config['MAIL_PORT'] = 465  # SMTP的加密SSL端口
app.config['MAIL_USE_SSL'] = True
# app.config['MAIL_USE_TLS'] = True
with open('mail.hikari') as f:
    data = eval(f.read())
    my_mail = data.get('mail')  # xxx@163.com
    my_pwd = data.get('password')  # 授权码, 不是密码
app.config['MAIL_USERNAME'] = my_mail
app.config['MAIL_PASSWORD'] = my_pwd

# app.config['FLASKY_MAIL_SUBJECT_PREFIX'] = '[Flasky]'
# app.config['FLASKY_MAIL_SENDER'] = 'hikari_python <{}>'.format(my_mail)
# app.config['FLASKY_ADMIN'] = '208343741@qq.com'
ADMIN = 'hikari_python@163.com'

db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
moment = Moment(app)
manager = Manager(app)

mail = Mail(app)
# -----------------


class NameForm(FlaskForm):  # 一个文本字段和一个提交按钮
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('提交')

# -------------------------


class Role(db.Model):
    __tablename__ = 'roles'  # 表名
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(64), unique=True)
    users = db.relationship('User', backref='role')  # , lazy='dynamic')

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

def send_async_mail(app,msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    # to为接收方,subject为邮件主题,template为渲染邮件正文的模板

    msg = Message(subject, sender=my_mail, recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)
    #mail.send(msg)
    t=Thread(target=send_async_mail,args=[app,msg])
    t.start()
    return t

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
            if ADMIN:
                send_mail(ADMIN, 'New User', 'mail/new_user', user=user)

        else:
            session['known'] = True
        session['name'] = form.name.data  # 获取字段data属性存入session
        form.name.data = ''  # 清空文本框
        return redirect(url_for('index'))  # 重定向, GET方式请求index
    return render_template('index.html', form=form, name=session.get('name'), known=session.get('known', False))


@app.route('/user/<name>')
def user(name):
    return render_template('user.html', name=name)


@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html'), 500


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role)


manager.add_command("shell", Shell(make_context=make_shell_context))
# -----------------
# 配置Flask-Migrate
migrate = Migrate(app, db)
manager.add_command('db', MigrateCommand)


if __name__ == '__main__':
    # 默认端口5000, 可以修改
    app.run(debug=True, port=8000)
    # manager.run()
