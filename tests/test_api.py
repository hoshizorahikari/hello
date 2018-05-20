import unittest
from app import db, create_app
from app.models import Role, User
from base64 import b64encode
import json


class APITestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()
        Role.insert_roles()
        self.client = self.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def get_api_headers(self, username, password):
        # 辅助方法,返回所有请求都要发送的通用首部,包含认证密令和MIME类型相关首部
        sb = '{}:{}'.format(username, password).encode('utf-8')
        s = b64encode(sb).decode('utf-8')
        return {
            'Authorization': 'Basic {}'.format(s),
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        }

    def test_no_auth(self):
        # 匿名用户无权访问401,但是之前是允许匿名用户访问
        # 所以app/api/authentication.py的verify_password()改成匿名用户访问返回False
        res = self.client.get('api/v1/blogs/', content_type='application/json')
        self.assertEqual(res.status_code, 401)

    def test_blogs(self):
        r = Role.query.filter_by(name='Moderator').first()
        self.assertIsNotNone(r)
        u = User(email='hikari@example.com', password='aaa111',
                 confirmed=True, username='hikari', role=r)
        db.session.add(u)
        db.session.commit()

        # 写一篇文章
        res = self.client.post('api/v1/blogs/',
                               headers=self.get_api_headers(
                                   'hikari@example.com', 'aaa111'),
                               data=json.dumps({'body': '我是**正文**...'}))
        self.assertEqual(res.status_code, 201)
        url = res.headers.get('Location')
        self.assertIsNotNone(url)
        # 获取刚才写的文章
        res = self.client.get(
            url, headers=self.get_api_headers(u.email, 'aaa111'))
        self.assertEqual(res.status_code, 200)
        dct = json.loads(res.get_data(as_text=True))
        self.assertEqual(dct['body'], '我是**正文**...')
        self.assertEqual(dct['body_html'],
                         '<p>我是<strong>正文</strong>...</p>')
