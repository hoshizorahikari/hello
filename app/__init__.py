from flask import Flask
from flask_bootstrap import Bootstrap
from flask_mail import Mail
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from config import config
from flask_login import LoginManager

bootstrap = Bootstrap()
mail = Mail()
moment = Moment()
db = SQLAlchemy()

login_manager = LoginManager()
# 用户会话保护等级, 可以设为None, 'basic', 'strong', 防止用户会话遭篡改
# 'strong': 记录客户端ip和浏览器User-Agent, 如果发生异动则登出用户
login_manager.session_protection = 'strong'
# auth蓝本的login视图
login_manager.login_view = 'auth.login'


def create_app(config_name):  # 工厂函数, 参数为配置名
    app = Flask(__name__)
    app.config.from_object(config[config_name])  # 导入配置
    config[config_name].init_app(app)

    bootstrap.init_app(app)
    mail.init_app(app)
    moment.init_app(app)
    db.init_app(app)

    login_manager.init_app(app)

    # 附加路由和自定义的错误页面
    from .main import main as main_blueprint
    app.register_blueprint(main_blueprint)
    from .auth import auth as auth_blueprint
    # url_prefix是可选, 蓝本所有路由添加前缀, 如/login变为/auth/login
    app.register_blueprint(auth_blueprint, url_prefix='/auth')
    return app  # 返回创建的程序示例
