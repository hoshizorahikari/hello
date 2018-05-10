import unittest
from flask import current_app
from app import create_app, db


class BasicsTestCase(unittest.TestCase):
    def setUp(self):  # 创建一个测试环境
        self.app = create_app('testing')
        self.app_context = self.app.app_context()  # 激活上下文
        self.app_context.push()
        db.create_all()  # 创建数据库


    def tearDown(self):
        # 删除数据库和上下文
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_app_exists(self):  # 测试app实例是否存在
        self.assertFalse(current_app is None)

    def test_app_is_testing(self):  # 程序是否在测试配置环境运行
        self.assertTrue(current_app.config['TESTING'])

