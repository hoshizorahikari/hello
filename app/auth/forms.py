from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User


class LoginForm(FlaskForm):
    email = StringField('邮箱', validators=[  # 电子邮箱数据必须, 长度限制, email验证函数
                        DataRequired(), Length(5, 64), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('登录')


class RegistrationForm(FlaskForm):
    email = StringField('邮箱', validators=[
                        DataRequired(), Length(5, 64), Email()])
    # username = StringField('用户名', validators=[DataRequired(), Length(
    #     2, 20), Regexp('^[A-Za-z][A-Za-z0-9_]{1,19}$', 0, '用户名只能是字母数字下划线！')])
    username = StringField('用户名', validators=[DataRequired(), Length(2, 20), Regexp('^\w{2,20}$', 0, '用户名只能是字母数字下划线！')])
    password = PasswordField(
        '输入密码', validators=[DataRequired(), EqualTo('password2', message='密码不一致！')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # 自定义验证函数, 如果表单类定义了validate_开头且跟着字段名的方法
    # 此方法与常规验证函数一起调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data).first():
            raise ValidationError('该邮箱已被注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在！')
