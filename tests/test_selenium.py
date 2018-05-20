from selenium import webdriver
import unittest
from app import db, create_app, fake
from app.models import User, Role, Blog
import time
from threading import Thread
import re


class SeleniumTestCase(unittest.TestCase):
    client = None

    @classmethod
    def setUpClass(cls):
        # setUpClass()类方法在此类全部测试运行之前执行
        options = webdriver.FirefoxOptions()
        options.set_headless()
        try:
            # 居然警告PhantomJS已经过时了?
            cls.client = webdriver.Firefox(firefox_options=options)
        except:
            pass
        if cls.client:  # 浏览器启动成功
            # 创建程序
            cls.app = create_app('testing')
            cls.app_context = cls.app.app_context()
            cls.app_context.push()
            # 禁止日志,保持输出简洁
            import logging
            logger = logging.getLogger('werkzeug')
            logger.setLevel('ERROR')
            # 创建数据库,使用虚拟数据填充
            db.create_all()
            Role.insert_roles()
            fake.gen_fake_users(10)
            fake.gen_fake_blogs(20)
            # 管理员
            admin_role = Role.query.filter_by(name='Admin').first()
            hikari = User(email='hikari@example.com',
                          username='hikari',
                          password='aaa111',
                          role=admin_role,
                          confirmed=True)
            db.session.add(hikari)
            db.session.commit()
            # 在子线程启动Flask服务器
            cls.server_thread = Thread(target=cls.app.run,
                                       kwargs={'debug': False})
            cls.server_thread.start()
            # 延时1s保证服务器正常运行
            time.sleep(1)

    @classmethod
    def tearDownClass(cls):
        # tearDownClass()类方法在此类全部测试运行之后执行
        if cls.client:
            # 所有测试结束,发送请求,关闭flask服务器和浏览器
            cls.client.get('http://localhost:5000/shutdown')
            cls.client.close()
            cls.server_thread.join()
            print('shutdown...')
            db.drop_all()  # 销毁数据库
            db.session.remove()
            cls.app_context.pop()  # 删除程序上下文

    def setUp(self):
        # setUp()方法在每个测试运行之前执行
        if not self.client:  # 没有成功启动浏览器,跳过测试
            self.skipTest('Web browser not available')

    def tearDown(self):
        pass

    def test_admin_home_page(self):
        # 个人偏好保存快照,因为no pic you say a jb...
        # GET请求首页
        self.client.get('http://localhost:5000/')
        time.sleep(1)
        self.client.save_screenshot('1_index.png')
        # 查看了源码才发现全是回车...这能玩?浪费时间额...
        self.assertTrue(re.search(r'<h1>\s+Hello,\s+Stranger\s+!\s+</h1>',
                                  self.client.page_source))

        # 登录页面
        self.client.find_element_by_link_text('登录').click()
        time.sleep(1)
        self.client.save_screenshot('2_login.png')
        self.assertIn('<h1>登录</h1>', self.client.page_source)

        # 登录
        self.client.find_element_by_name(
            'email').send_keys('hikari@example.com')
        self.client.find_element_by_name('password').send_keys('aaa111')
        self.client.find_element_by_name('submit').click()
        time.sleep(1)
        self.client.save_screenshot('3_after_login.png')
        self.assertTrue(re.search(r'<h1>\s+Hello,\s+hikari\s+!\s+</h1>',
                                  self.client.page_source))

        # 用户资料页面
        self.client.find_element_by_link_text('Profile').click()
        time.sleep(1)
        self.client.save_screenshot('4_profile.png')
        self.assertIn('<h1>hikari</h1>', self.client.page_source)
