import os

# flask程序根目录
basedir = os.path.abspath(os.path.dirname(__file__))
my_mail, my_pwd = None, None
with open('mail.hikari') as f:
    data = eval(f.read())
    my_mail = data.get('mail')  # xxx@qq.com
    my_pwd = data.get('password')  # 授权码, 不是密码


def get_db_url(a):
    return os.environ.get('{}DATABASE_URL'.format(a.upper())) or \
        'sqlite:///{}'.format(os.path.join(basedir, '{}data.sqlite'.format(a)))
    # return os.environ.get('{}DATABASE_URL'.format(a.upper())) or \
    #     'mysql+pymysql://root:mysql@localhost:3306/{}myblog'.format(a)


class Config():  # 父类通用配置
    # 敏感信息从环境变量获取, 但还是给了默认值
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'hoshizora rin'
    MAIL_SERVER = os.environ.get('MAIL_SERVER') or 'smtp.qq.com'
    MAIL_PORT = int(os.environ.get('MAIL_PORT', 465))  # SMTP的加密SSL端口
    MAIL_USE_SSL = True  # SSL
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME') or my_mail
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD') or my_pwd
    SQLALCHEMY_COMMIT_ON_TEARDOWN = True
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    # FLASKY_MAIL_SUBJECT_PREFIX = '[Flasky]'
    # FLASKY_MAIL_SENDER = 'Flasky Admin <flasky@example.com>'
    FLASKY_ADMIN = os.environ.get('FLASKY_ADMIN') or my_mail
    BLOGS_PER_PAGE = 20
    FOLLOWERS_PER_PAGE = 50
    COMMENTS_PER_PAGE = 30
    SQLALCHEMY_RECORD_QUERIES = True  # Flask-SQLAlchemy启用记录查询统计数字功能
    SLOW_DB_QUERY_TIME = 0.5  # 缓慢查询的阈值

    USERS_PER_PAGE = 50

    @staticmethod
    def init_app(app):  # 对当前环境配置初始化
        pass

# 3种环境使用不同数据库


class DevelopmentConfig(Config):  # 开发专用配置
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = get_db_url('dev_')
    # os.environ.get('DEV_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-dev.sqlite')


class TestingConfig(Config):  # 测试专用配置
    TESTING = True
    SQLALCHEMY_DATABASE_URI = get_db_url('test_')
    # os.environ.get('TEST_DATABASE_URL') or 'sqlite:///' + os.path.join(basedir, 'data-test.sqlite')
    WTF_CSRF_ENABLED = False  # 测试环境中禁用CSRF保护


class ProductionConfig(Config):  # 生产专用配置
    SQLALCHEMY_DATABASE_URI = get_db_url('')

    @classmethod
    def init_app(cls, app):
        # 所有配置类都有init_app()静态方法,在create_app()中调用
        Config.init_app(app)
        # 用管理员的email把错误发送给管理员的小号
        import logging
        from logging.handlers import SMTPHandler
        credentials = None
        secure = None
        if getattr(cls, 'MAIL_USERNAME', None) is not None:
            credentials = (cls.MAIL_USERNAME, cls.MAIL_PASSWORD)
            if getattr(cls, 'MAIL_USE_TLS', None):
                secure = ()
        mail_handler = SMTPHandler(
            mailhost=(cls.MAIL_SERVER, cls.MAIL_PORT),
            fromaddr=cls.MAIL_USERNAME,
            toaddrs=['208343741@qq.com'],
            subject='hikari app出错啦!',
            credentials=credentials,
            secure=secure)
        # ERROR等级只有发生严重错误时才发送邮件
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)


config = {
    'development': DevelopmentConfig,
    'testing': TestingConfig,
    'production': ProductionConfig,

    'default': DevelopmentConfig  # 默认开发环境的配置
}
