import unittest
from app.models import Permission, Role, User, AnonymousUser
from app import db, create_app
import time
from app.models import Role




class UserModelTestCase(unittest.TestCase):
    # test_basics里已经有setUP和tearDown了, 此处不需要,写了报错
    # 为什么后来出现问题,添加setUp和tearDown又成功了...
    def setUp(self):  # 创建一个测试环境
        self.app = create_app('testing')
        self.app_context = self.app.app_context()  # 激活上下文
        self.app_context.push()
        db.create_all()  # 创建数据库
        Role.insert_roles()

    def tearDown(self):
        # 删除数据库和上下文
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):  # 测试设置密码
        u = User(password='maki')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):  # 测试不能获取密码
        u = User(password='maki')
        with self.assertRaises(AttributeError):
            u.password

    def test_password_verification(self):  # 测试密码认证
        u = User(password='maki')
        self.assertTrue(u.verify_password('maki'))
        self.assertFalse(u.verify_password('rin'))

    def test_password_salts_are_random(self):  # 测试是否随机撒盐
        u = User(password='maki')
        u2 = User(password='maki')
        self.assertFalse(u.password_hash == u2.password_hash)

    def test_valid_confirmation_token(self):  # 测试正确的确认令牌
        u = User(password='maki')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self):  # 测试用别人的确认令牌
        u1 = User(password='maki')
        u2 = User(password='rin')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()  # 要commit(), 不然失败?
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self):  # 测试过期令牌
        u = User(password='maki')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self):  # 重置密码的令牌
        u = User(password='maki')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'rin'))
        self.assertTrue(u.verify_password('rin'))

    def test_invalid_reset_token(self):  # 无效的重置密码令牌
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))

    def test_valid_email_change_token(self):  # 修改邮箱的令牌
        u = User(email='john@example.com', password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_email_change_token('susan@example.org')
        self.assertTrue(u.change_email(token))
        self.assertTrue(u.email == 'susan@example.org')

    def test_invalid_email_change_token(self):  # 无效的修改邮箱令牌
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u1.generate_email_change_token('david@example.net')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_duplicate_email_change_token(self):  # 修改的邮箱已经存在
        u1 = User(email='john@example.com', password='cat')
        u2 = User(email='susan@example.org', password='dog')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit()
        token = u2.generate_email_change_token('john@example.com')
        self.assertFalse(u2.change_email(token))
        self.assertTrue(u2.email == 'susan@example.org')

    def test_user_role(self):  # 普通用户的权限
        u = User(email='john@example.com', password='cat')
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_moderator_role(self):  # 协助管理员的权限
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_admin_role(self):  # 管理员权限
        r = Role.query.filter_by(name='Admin').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertTrue(u.can(Permission.ADMIN))

    def test_anonymous_user(self):  # 匿名用户权限
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))
