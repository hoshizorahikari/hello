import unittest
from app.models import User
from app import db
import time

# 测试用户模型的密码散列化


class UserModelTestCase(unittest.TestCase):
    # test_basics里已经有setUP和tearDown了, 此处不需要,写了报错
    # def setUP(self):
    #     self.app = create_app('testing')
    #     self.app_context = self.app.app_context()
    #     self.app_context.push()
    #     db.create_all()

    # def tearDown(self):
    #     db.session.remove()
    #     db.drop_all()
    #     self.app_context.pop()

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

    
    def test_valid_confirmation_token(self):# 测试正确的确认令牌
        u = User(password='maki')
        db.session.add(u)
        db.session.commit() 
        token = u.generate_confirmation_token()
        self.assertTrue(u.confirm(token))

    def test_invalid_confirmation_token(self): # 测试用别人的确认令牌
        u1 = User(password='maki')
        u2 = User(password='rin')
        db.session.add(u1)
        db.session.add(u2)
        db.session.commit() # 要commit(), 不然失败?
        token = u1.generate_confirmation_token()
        self.assertFalse(u2.confirm(token))

    def test_expired_confirmation_token(self): # 测试令牌过时
        u = User(password='maki')
        db.session.add(u)
        db.session.commit()
        token = u.generate_confirmation_token(1)
        time.sleep(2)
        self.assertFalse(u.confirm(token))

    def test_valid_reset_token(self): # 重置令牌
        u = User(password='maki')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertTrue(User.reset_password(token, 'rin'))
        self.assertTrue(u.verify_password('rin'))

    def test_invalid_reset_token(self):
        u = User(password='cat')
        db.session.add(u)
        db.session.commit()
        token = u.generate_reset_token()
        self.assertFalse(User.reset_password(token + 'a', 'horse'))
        self.assertTrue(u.verify_password('cat'))


