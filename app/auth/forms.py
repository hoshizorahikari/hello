from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length, Email, Regexp, EqualTo
from wtforms import ValidationError
from ..models import User

lst = ['高坂穂乃果', '絢瀬絵里', '南ことり', '園田海未', '星空凛', '西木野真姫', '東條希', '小泉花陽', '矢澤にこ',
       '高海千歌', '桜内梨子', '松浦果南', '黒澤ダイヤ', '渡辺曜', '津島善子', '国木田花丸', '小原鞠莉', '黒澤ルビイ',
       '上原歩夢', '中須かすみ', '桜坂しずく', '朝香果林', '宮下愛', '近江彼方', '優木せつ菜', 'エマ・ヴェルデ', '天王寺璃奈', ]


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
    username = StringField('用户名', validators=[DataRequired(), Length(
        2, 20), Regexp('^\w{2,20}$', 0, '用户名只能是字母数字下划线！')])
    password = PasswordField(
        '输入密码', validators=[DataRequired(), EqualTo('password2', message='密码不一致！')])
    password2 = PasswordField('确认密码', validators=[DataRequired()])
    submit = SubmitField('注册')

    # 自定义验证函数, 如果表单类定义了validate_开头且跟着字段名的方法
    # 此方法与常规验证函数一起调用
    def validate_email(self, field):
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被注册！')

    def validate_username(self, field):
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('用户名已经存在！')
        if field.data.lower() in lst:
            raise ValidationError('该用户名无法使用！')


class ChangePasswordForm(FlaskForm):
    # 修改密码表单类
    old_password = PasswordField('输入原密码', validators=[DataRequired()])
    password = PasswordField('设置新密码', validators=[
                             DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class PasswordResetRequestForm(FlaskForm):
    # 重设密码请求表单
    email = StringField(
        '邮箱', validators=[DataRequired(), Length(5, 64), Email()])
    submit = SubmitField('重设密码')


class PasswordResetForm(FlaskForm):
    # 重设密码表单
    password = PasswordField('设置新密码', validators=[
                             DataRequired(), EqualTo('password2', message='密码不一致')])
    password2 = PasswordField('确认新密码', validators=[DataRequired()])
    submit = SubmitField('确认')


class ChangeEmailForm(FlaskForm):
    # 修改邮箱表单类
    email = StringField('新邮箱', validators=[
                        DataRequired(), Length(5, 64), Email()])
    password = PasswordField('请输入密码', validators=[DataRequired()])
    submit = SubmitField('确认')

    def validate_email(self, field):
        # 如果输入邮箱已被注册,抛出异常
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('该邮箱已被注册！')
