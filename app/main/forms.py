from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, BooleanField, SelectField
from wtforms.validators import DataRequired, Length, Email, Regexp
from ..models import Role, User
from wtforms import ValidationError
from flask_pagedown.fields import PageDownField


class NameForm(FlaskForm):  # 一个文本字段和一个提交按钮
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('提交')


class EditProfileForm(FlaskForm):  # 用户编辑资料的表单
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    submit = SubmitField('提交')


class EditProfileAdminForm(FlaskForm):  # 管理员使用的资料编辑表单类
    email = StringField(
        '邮箱', validators=[DataRequired(), Length(5, 64), Email()])
    username = StringField('用户名', validators=[
        DataRequired(), Length(2, 20),
        Regexp(r'^\w{2,20}$', 0, '不能有奇怪的字符哦！')])
    confirmed = BooleanField('认证与否')
    # select下拉菜单,选项在构造函数choice属性设置,是二元元组组成的列表
    role = SelectField('权限', coerce=int)
    name = StringField('真实姓名', validators=[Length(0, 64)])
    location = StringField('所在地', validators=[Length(0, 64)])
    about_me = TextAreaField('个人简介')
    image = StringField('头像链接')
    submit = SubmitField('提交')

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # 从Role模型获取角色id和名称,组成二元元组的列表
        self.role.choices = [(role.id, role.name)
                             for role in Role.query.order_by(Role.name).all()]
        self.user = user

    def validate_email(self, field):
        # 如果输入不是原邮箱,但已经存在,抛出错误
        if field.data.lower() != self.user.email \
                and User.query.filter_by(email=field.data).first():
            raise ValidationError('邮箱已经存在！')

    def validate_username(self, field):
        # 如果输入不是原用户名,但已经存在,抛出错误
        if field.data.lower() != self.user.username \
                and User.query.filter_by(username=field.data).first():
            raise ValidationError('用户名已经存在！')


class BlogForm(FlaskForm):  # 撰写博客表单类
    title = StringField('标题', validators=[DataRequired()])
    tags = StringField('标签', validators=[DataRequired()])
    body = PageDownField('写点什么吧...', validators=[DataRequired()])
    submit = SubmitField('提交')


class CommentForm(FlaskForm):  # 写评论的表单类
    body = PageDownField('写点什么吧...', validators=[DataRequired()])
    submit = SubmitField('提交')


	
