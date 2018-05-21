from flask import current_app, url_for
from flask_login import AnonymousUserMixin, UserMixin
from itsdangerous import TimedJSONWebSignatureSerializer as Slzer
from werkzeug.security import check_password_hash, generate_password_hash

from flask import current_app
from . import db, login_manager
from datetime import datetime
import hashlib
# from flask import request
from markdown import markdown
import bleach

from app.exceptions import ValidationError


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
        user = [Permission.FOLLOW, Permission.COMMENT]
        writer = user.append(Permission.WRITE)
        mod = writer.append(Permission.MODERATE)
        admin = mod.append(Permission.ADMIN)
        roles = {
            'User': uuser,
            'Writer': writer,
            'Moderator': mod,
            'Admin': admin,
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


class Follow(db.Model):  # 关注功能的关联表模型
    __tablename__ = 'follows'
    follower_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    followed_id = db.Column(db.Integer, db.ForeignKey('users.id'),
                            primary_key=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)


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

    image = db.Column(db.String(128))  # 头像链接
    blogs = db.relationship('Blog', backref='author', lazy='dynamic')
    # 两个一对多关系实现多对多关系
    # 该用户关注的大神
    followed = db.relationship('Follow',
                               foreign_keys=[Follow.follower_id],  # 消除外键歧义
                               # 回引Follow模型
                               # 该用户甘愿当此人的小弟
                               backref=db.backref('follower', lazy='joined'),
                               lazy='dynamic',
                               cascade='all, delete-orphan')
    # 关注该用户的萌新
    followers = db.relationship('Follow',
                                foreign_keys=[Follow.followed_id],
                                # 将该用户视为大神的用户
                                backref=db.backref('followed', lazy='joined'),
                                lazy='dynamic',
                                cascade='all, delete-orphan')

    comments = db.relationship('Comment', backref='author', lazy='dynamic')
    disabled = db.Column(db.Boolean, default=False)  # 封禁用户

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
        if 'gravatar.com' in self.image:  # 自定义头像的不改
            self.image = self.gravatar(size=256)  # 修改邮箱后重新生成头像
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
        self.image = self.gravatar(size=256)

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
        url = 'https://www.gravatar.com/avatar'
        md5 = hashlib.md5(self.email.encode('utf-8')).hexdigest()
        return '{}/{}?s={}&d={}&r={}'.format(url, md5, size, default, rating)

    def follow(self, user):
        # 关注某用户(如果没有关注)
        if not self.is_following(user) and self != user:
            f = Follow(followed=user)
            self.followed.append(f)

    def unfollow(self, user):
        # 取消关注(如果已经关注)
        f = self.followed.filter_by(followed_id=user.id).first()
        if f:
            # 删除Follow对象,销毁联系
            self.followed.remove(f)

    def is_following(self, user):
        # user是不是该用户关注的大神
        if user.id is None:
            return False
        return self.followed.filter_by(
            followed_id=user.id).first() is not None

    def is_followed_by(self, user):
        # user是不是关注该用户的萌新
        if user.id is None:
            return False
        return self.followers.filter_by(
            follower_id=user.id).first() is not None

    @property
    def followed_blogs(self):
        # 关注的大神的所有文章
        return Blog.query.filter_by(disabled=False).join(Follow, Follow.followed_id == Blog.author_id)\
            .filter(Follow.follower_id == self.id)

    @staticmethod
    def add_self_follows():
        for user in User.query.all():
            if not user.is_following(user):
                user.follow(user)
                db.session.add(user)
                db.session.commit()

    def gen_auth_token(self, expiration):
        # 以用户id生成签名令牌
        s = Slzer(current_app.config['SECRET_KEY'], expires_in=expiration)
        return s.dumps({'id': self.id}).decode('utf-8')

    @staticmethod
    def verify_auth_token(token):
        # 静态方法因为只有解码令牌后才知道用户是谁
        s = Slzer(current_app.config['SECRET_KEY'])
        try:
            data = s.loads(token)
        except:
            return
        # 返回id对应用户对象
        return User.query.get(data['id'])

    def to_json(self):
        return {
            'url': url_for('api.get_user', id=self.id),
            'username': self.username,
            'member_since': self.member_since,
            'last_seen': self.last_seen,
            'blogs_url': url_for('api.get_user_blogs', id=self.id),
            'followed_blogs_url': url_for('api.get_user_followed_blogs',
                                          id=self.id),
            'blog_count': self.blogs.count()
        }


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


class Blog(db.Model):
    __tablename__ = 'blogs'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)  # 博客正文
    body_html = db.Column(db.Text)  # 博客正文HTML代码
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)  # 创建时间
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    comments = db.relationship('Comment', backref='blog', lazy='dynamic')
    disabled = db.Column(db.Boolean, default=False)  # 逻辑删除文章
    title = db.Column(db.String(64), default='no title')
    summary = db.Column(db.String(160), default='no summary')

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # body字段渲染成HTML保存到body_html
        # allowed_tags = ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code',
        #                 'em', 'i', 'li', 'ol', 'pre', 'strong', 'ul',
        #                 'h1', 'h2', 'h3', 'p']
        exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite',
                'markdown.extensions.tables', 'markdown.extensions.toc']
        target.body_html = markdown(value, extensions=exts)

        # target.body_html = bleach.linkify(bleach.clean(
        #     markdown(value, output_format='html'),
        #     tags=allowed_tags, strip=True))
    def to_json(self):
        return {
            'url': url_for('api.get_blog', id=self.id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
            'comments_url': url_for('api.get_blog_comments', id=self.id),
            'comment_count': self.comments.count()
        }

    @staticmethod
    def from_json(blog_json):
        body = blog_json.get('body')
        if body is None or body == '':
            raise ValidationError('博客文章木有正文！')
        return Blog(body=body)


# on_changed_body注册在body字段, SQLAlchemy 'set'事件的监听程序
# 只要body字段设了新值,函数自动被调用
db.event.listen(Blog.body, 'set', Blog.on_changed_body)


class Comment(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    body = db.Column(db.Text)  # 评论正文
    body_html = db.Column(db.Text)  # 评论正文HTML代码
    timestamp = db.Column(db.DateTime, index=True,
                          default=datetime.utcnow)  # 评论时间
    disabled = db.Column(db.Boolean, default=False)  # 查禁不当评论
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'))
    blog_id = db.Column(db.Integer, db.ForeignKey('blogs.id'))

    @staticmethod
    def on_changed_body(target, value, oldvalue, initiator):
        # body字段渲染成HTML保存到body_html

        allowed_tags = ['a', 'abbr', 'acronym', 'b', 'code', 'em', 'i',
                        'strong']
        exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite',
                'markdown.extensions.tables', 'markdown.extensions.toc']
        target.body_html = bleach.clean(
            markdown(value, extensions=exts), tags=allowed_tags, strip=True)
        # exts = ['markdown.extensions.extra', 'markdown.extensions.codehilite',
        #         'markdown.extensions.tables', 'markdown.extensions.toc']
        # target.body_html = markdown(value, extensions=exts)

        # target.body_html = bleach.linkify(bleach.clean(
        #     markdown(value, output_format='html'),
        #     tags=allowed_tags, strip=True))

    def to_json(self):
        return {
            'url': url_for('api.get_comment', id=self.id),
            'blog_url': url_for('api.get_blog', id=self.blog_id),
            'body': self.body,
            'body_html': self.body_html,
            'timestamp': self.timestamp,
            'author_url': url_for('api.get_user', id=self.author_id),
        }

    @staticmethod
    def from_json(comment_json):
        body = comment_json.get('body')
        if body is None or body == '':
            raise ValidationError('木有评论！')
        return Comment(body=body)


# on_changed_body注册在body字段, SQLAlchemy 'set'事件的监听程序
# 只要body字段设了新值,函数自动被调用
db.event.listen(Comment.body, 'set', Comment.on_changed_body)
