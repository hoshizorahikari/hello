import unittest
from app import create_app, db
from app.models import User, Role


class FlaskClientTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        # Flask测试客户端对象
        self.client = self.app.test_client(use_cookies=True)

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_home_page(self):
        # GET方法访问首页,返回FlaskResponse对象
        response = self.client.get('/')
        # 响应状态码是不是200?
        self.assertEqual(response.status_code, 200)
        # response.data获取响应的二进制数据
        self.assertTrue(b'Stranger' in response.data)

    def test_register_and_login(self):
        # 注册新账号
        response = self.client.post('/auth/register', data={
            'email': 'hikari@example.com',
            'username': 'hikari_test',
            'password': 'aaa111',
            'password2': 'aaa111'
        })
        self.assertEqual(response.status_code, 302)
        # 使用新账号登录,follow_redirects=True自动向重定向的URL发送GET请求
        # 其返回状态码不是302而是重定向URL返回的响应,此处是200
        response = self.client.post('/auth/login', data={
            'email': 'hikari@example.com',
            'password': 'aaa111'
        }, follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('你好, hikari_test!'.encode('utf-8') in response.data)
        self.assertTrue('你的账号还没激活!'.encode('utf-8') in response.data)
        # 发送确认令牌激活账号,测试中处理电子邮件不简单,所以直接获取token拼接URL
        u = User.query.filter_by(email='hikari@example.com').first()
        token = u.generate_confirmation_token()
        response = self.client.get('auth/confirm/{}'.format(token),
                                   follow_redirects=True)
        # u.confirm(token)  # 此句没必要吧,GET请求认证URL就已经确认了吧?
        self.assertTrue(response.status_code, 200)
        self.assertTrue('你的账号已通过认证！'.encode('utf-8') in response.data)
        # 退出
        response = self.client.get('/auth/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('你已经退出...'.encode('utf-8') in response.data)
