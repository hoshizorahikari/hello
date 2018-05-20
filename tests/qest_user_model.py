import unittest
from app.models import Permission, Role, User, AnonymousUser, Permission, Follow
from app import db, create_app
import time
from datetime import datetime


class UserModelTestCase(unittest.TestCase):
    # test_basics里已经有setUP和tearDown了, 此处不需要,写了报错
    # 为什么后来出现问题,添加setUp和tearDown又成功了...
    def setUp(self):  # 创建一个测试环境
        self.app = create_app('testing')
        self.app_context = self.app.app_context()  # 激活上下文
        self.app_context.push()
        db.create_all()  # 创建数据库
        Role.insert_roles()
        self.admin = Role.query.filter_by(name='Admin').first()
        self.u = User(email='2091248018@qq.com', password='1234',
                      username='hikari', confirmed=True, role=self.admin)
        self.u1 = User(email='maki@qq.com',
                       password='makimakima', username='maki')
        self.u2 = User(email='rin@qq.com', password='koyachin', username='rin')
        db.session.add_all([self.u, self.u1, self.u2])
        db.session.commit()

    def tearDown(self):
        # 删除数据库和上下文
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_password_setter(self):  # 测试设置密码
        self.assertTrue(self.u is not None)

    def test_no_password_getter(self):  # 测试不能获取密码
        with self.assertRaises(AttributeError):
            self.u.password

    def test_password_verification(self):  # 测试密码认证
        self.assertTrue(self.u.verify_password('1234'))
        self.assertFalse(self.u.verify_password('rin'))

    def test_password_salts_are_random(self):  # 测试是否随机撒盐
        u=User(email='maki2@qq.com', password='makimakima', username='maki2')
        self.assertFalse(u.password_hash == self.u.password_hash)

    def test_valid_confirmation_token(self):  # 测试正确的确认令牌
        token = self.u1.generate_confirmation_token()
        self.assertTrue(self.u1.confirm(token))

    def test_invalid_confirmation_token(self):  # 测试用别人的确认令牌
        token = self.u1.generate_confirmation_token()
        self.assertFalse(self.u2.confirm(token))

    def test_expired_confirmation_token(self):  # 测试过期令牌
        token = self.u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(self.u.confirm(token))

    def test_valid_reset_token(self):  # 重置密码的令牌
        token = self.u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'aaa111'))
        self.assertTrue(self.u.verify_password('aaa111'))
        token = self.u.generate_reset_token()
        self.assertTrue(User.reset_password(token, '1234'))
        self.assertTrue(self.u.verify_password('1234'))

    def test_invalid_reset_token(self):  # 无效的重置密码令牌
        token = self.u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'haha'))
        self.assertTrue(self.u.verify_password('1234'))

    def test_valid_email_change_token(self):  # 修改邮箱的令牌
        token = self.u.generate_email_change_token('208343741@qq.com')
        self.assertTrue(self.u.change_email(token))
        self.assertTrue(self.u.email == '208343741@qq.com')
        token = self.u.generate_email_change_token('2091248018@qq.com')
        self.assertTrue(self.u.change_email(token))
        self.assertTrue(self.u.email == '2091248018@qq.com')

    def test_invalid_email_change_token(self):  # 无效的修改邮箱令牌
        token = self.u1.generate_email_change_token('maki@qq.com')
        self.assertFalse(self.u2.change_email(token))
        self.assertTrue(self.u2.email == 'rin@qq.com')

    def test_duplicate_email_change_token(self):  # 修改的邮箱已经存在
        token = self.u2.generate_email_change_token('maki@qq.com')
        self.assertFalse(self.u2.change_email(token))
        self.assertTrue(self.u2.email == 'rin@qq.com')

    def test_user_role(self):  # 普通用户的权限

        self.assertTrue(self.u1.can(Permission.FOLLOW))
        self.assertTrue(self.u1.can(Permission.COMMENT))
        self.assertFalse(self.u1.can(Permission.WRITE))
        self.assertFalse(self.u1.can(Permission.MODERATE))
        self.assertFalse(self.u1.can(Permission.ADMIN))

    def test_moderator_role(self):  # 协助管理员的权限
        r = Role.query.filter_by(name='Moderator').first()
        u = User(email='john@example.com', password='cat', role=r)
        self.assertTrue(u.can(Permission.FOLLOW))
        self.assertTrue(u.can(Permission.COMMENT))
        self.assertTrue(u.can(Permission.WRITE))
        self.assertTrue(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))

    def test_admin_role(self):  # 管理员权限
        self.assertTrue(self.u.can(Permission.FOLLOW))
        self.assertTrue(self.u.can(Permission.COMMENT))
        self.assertTrue(self.u.can(Permission.WRITE))
        self.assertTrue(self.u.can(Permission.MODERATE))
        self.assertTrue(self.u.can(Permission.ADMIN))

    def test_anonymous_user(self):  # 匿名用户权限
        u = AnonymousUser()
        self.assertFalse(u.can(Permission.FOLLOW))
        self.assertFalse(u.can(Permission.COMMENT))
        self.assertFalse(u.can(Permission.WRITE))
        self.assertFalse(u.can(Permission.MODERATE))
        self.assertFalse(u.can(Permission.ADMIN))


    def test_to_json(self):

        with self.app.test_request_context('/'):
            user_json = self.u.to_json()
        expected_keys = ['url', 'username', 'member_since', 'last_seen',
                         'blogs_url', 'followed_blogs_url', 'blog_count']
        self.assertEqual(sorted(user_json.keys()), sorted(expected_keys))
        self.assertEqual('/api/v1/users/' + str(self.u.id), user_json['url'])

