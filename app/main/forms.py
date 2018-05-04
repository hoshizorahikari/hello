from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class NameForm(FlaskForm):  # 一个文本字段和一个提交按钮
    name = StringField('你的名字是？', validators=[DataRequired()])
    submit = SubmitField('提交')
