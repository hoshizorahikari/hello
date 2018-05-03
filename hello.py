from flask import Flask, redirect, render_template, session, url_for, flash
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

# from flask_moment import Moment
# from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'hoshizora rin'


bootstrap = Bootstrap(app)
# moment = Moment(app)

# ----------------


class NameForm(FlaskForm):  # 一个文本字段和一个提交按钮
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('提交')


@app.route('/', methods=['GET', 'POST'])  # 支持GET和POST
def index():
    form = NameForm()
    if form.validate_on_submit():  # 提交表单,数据被验证函数接受
        old_name = session.get('name')  # 获取session已有name
        if old_name and old_name != form.name.data:
            flash('你似乎改名字了！')
        session['name'] = form.name.data  # 获取字段data属性存入session
        return redirect(url_for('index'))  # 重定向,GET方式请求index
    return render_template('index.html', form=form, name=session.get('name'))


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


if __name__ == '__main__':
    # 默认端口5000, 可以修改
    app.run(debug=True, port=8000)
