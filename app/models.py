from flask import current_app
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Slzer
from werkzeug.security import check_password_hash, generate_password_hash

from flask import current_app
from . import db, login_manager
from datetime import datetime
import hashlib
# from flask import request


class Permission:  # 用户权限常量
    FOLLOW = 1
    COMMENT = 2
    WRITE = 4
    MODERATE = 8
    ADMIN = 16


class Role(db.Model):
    __tablename__ = 'roles'  # 表名
    id = db.Column(db.Integer, primary_key=True)  # 主键
    name = db.Column(db.String(64), unique=True)  # 角色名
    # 只有一个角色default字段要设为True,其他为False
    default = db.Column(db.Boolean, default=False, index=True)
    permissions = db.Column(db.Integer)
    users = db.relationship('User', backref='role', lazy='dynamic')

    def __repr__(self):
        return '<Role %r>' % self.name

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.permissions is None:
            self.permissions = 0

    @staticmethod
    def insert_roles():
        # 角色字符串为键,权限常量列表为值
        roles = {
            'User': [Permission.FOLLOW, Permission.COMMENT],
            'Moderator': [Permission.FOLLOW, Permission.COMMENT,
                          Permission.WRITE, Permission.MODERATE],
            'Admin': [Permission.FOLLOW, Permission.COMMENT,
                      Permission.WRITE, Permission.MODERATE, Permission.ADMIN],
        }
        default_role = 'User'
        for k, v in roles.items():
            # 对于每个角色,如果数据库不存在添加之;每个角色重设权限
            role = Role.query.filter_by(name=k).first()
            if role is None:
                role = Role(name=k)
            role.reset_permissions()
            for i in v:
                role.add_permission(i)
            # 普通用户角色的default为True
            role.default = (role.name == default_role)
            db.session.add(role)
        db.session.commit()

    def has_permission(self, p):
        # 指定权限位是不是1?
        return (self.permissions & p) == p

    def add_permission(self, p):
        # 如果没有此权限,添加之
        if not self.has_permission(p):
            self.permissions += p

    def remove_permission(self, p):
        # 如果有此权限,删除之
        if self.has_permission(p):
            self.permissions -= p

    def reset_permissions(self):
        # 权限重置为0
        self.permissions = 0


class User(UserMixin, db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)  # 主键
    email = db.Column(db.String(64), unique=True, index=True)  # 邮箱
    username = db.Column(db.String(64), unique=True, index=True)  # 用户名
    password_hash = db.Column(db.String(128))  # 密码的散列值
    role_id = db.Column(db.Integer, db.ForeignKey(
        'roles.id'))  # 外键, roles表中的id
    confirmed = db.Column(db.Boolean, default=False)
    # 新添加字段
    name = db.Column(db.String(64))  # 真实姓名
    location = db.Column(db.String(64))  # 所在地
    # Text()大文本,不需要指定最大长度
    about_me = db.Column(db.Text())  # 自我介绍
    # utcnow没有(),default可以接收函数作为默认值,每次需要默认值都会调用utcnow()
    member_since = db.Column(db.DateTime(), default=datetime.utcnow)  # 注册时间

    last_seen = db.Column(db.DateTime(), default=datetime.utcnow)  # 最后访问日期

    image = db.Column(db.String) = db.Column(db.String(128)) # 头像链接

    # password属性只可写不可读, 因为获取散列值没有意义, 无法还原密码

    @property
    def password(self):
        raise AttributeError('password is not a readable attribute')

    @password.setter
    def password(self, pwd):
        self.password_hash = generate_password_hash(pwd)

    def verify_password(self, pwd):  # 校验密码
        return check_password_hash(self.password_hash, pwd)

    def __repr__(self):
        return '<User %r>' % self.username

    def generate_confirmation_token(self, expiration=3600):
        # 生成确认令牌字符串, 默认有效时间1h
        s = Slzer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'confirm': self.id}).decode('utf-8')

    def confirm(self, token):
        # 检验令牌, 通过则confirmed字段设为True
        s = Slzer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        if data.get('confirm') != self.id:
            return False
        self.confirmed = True
        db.session.add(self)
        return True

    def generate_reset_token(self, expiration=3600):
        # 生成重置令牌字符串, 默认有效时间1h
        s = Slzer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps({'reset': self.id}).decode('utf-8')

    @staticmethod
    def reset_password(token, new_password):
        s = Slzer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        # 根据令牌获取用户id,查询该用户
        user = User.query.get(data.get('reset'))
        if user is None:  # 用户不存在
            return False
        # 用户存在,重置密码
        user.password = new_password
        db.session.add(user)
        return True

    def generate_email_change_token(self, new_email, expiration=3600):
        # 生成修改邮箱令牌字符串, 默认有效时间1h
        s = Slzer(current_app.config['SECRET_KEY'], expiration)
        return s.dumps(
            {'change_email': self.id, 'new_email': new_email}).decode('utf-8')

    def change_email(self, token):
        s = Slzer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token.encode('utf-8'))
        except:
            return False
        # 令牌不属于当前用户,新邮箱为None,新邮箱已经存在都修改失败
        if data.get('change_email') != self.id:
            return False
        new_email = data.get('new_email')
        if new_email is None:
            return False
        if self.query.filter_by(email=new_email).first() is not None:
            return False
        self.email = new_email
        self.image = self.gravatar()  # 修改邮箱后重新生成头像
        db.session.add(self)
        return True

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        if self.role is None:
            # 是管理员的邮箱,该用户设为admin角色
            if self.email == current_app.config['FLASKY_ADMIN']:
                self.role = Role.query.filter_by(name='Admin').first()
            # 如果该用户还是没有角色,设为默认普通用户
            if self.role is None:
                self.role = Role.query.filter_by(default=True).first()
        self.image = self.gravatar()

    def can(self, p):
        # 用户不为None且拥有权限p
        return self.role is not None and self.role.has_permission(p)

    def is_admin(self):
        # 检查用户是不是管理员
        return self.can(Permission.ADMIN)

    def ping(self):
        self.last_seen = datetime.utcnow()
        db.session.add(self)

    def gravatar(self, size=100, default='monsterid', rating='g'):
        # 根据邮箱的md5获取头像URL
        url = 'https://secure.gravatar.com/avatar'
        md5 = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{}/{}?s={}&d={}&r={}'.format(url, md5, size, default, rating)


class AnonymousUser(AnonymousUserMixin):
    def can(self, p):
        return False

    def is_admin(self):
        return False


login_manager.anonymous_user = AnonymousUser


@login_manager.user_loader
def load_user(user_id):
    # user_id为Unicode字符串表示的用户标识符, 如果有此用户返回用户对象; 否则返回None
    return User.query.get(int(user_id))
