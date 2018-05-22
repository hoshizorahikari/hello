import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    # 覆盖检测引擎, branch开启分支覆盖分析,检查每个条件语句True和False
    # 分支是否都执行;include限定文件分析范围
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User, Role, Permission, Blog, Comment, Follow,Tag
import app.fake as fake
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# app_context = app.app_context()  # 激活上下文
# app_context.push()
# db.create_all()  # 创建数据库

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Blog=Blog, fake=fake, Comment=Comment,Tag=Tag)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


# @manager.command
# def test():
#     """单元测试"""
#     import unittest
#     # 寻找测试文件的目录
#     tests = unittest.TestLoader().discover('tests')
#     # 读取测试文件并运行测试
#     unittest.TextTestRunner(verbosity=2).run(tests)

@manager.command
def test(coverage=False):
    """单元测试,test命令的选项就是test()函数的参数"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
        # 设定该环境变量后重启脚本?再次运行,上面代码能获取该环境变量,可以启动覆盖检测
        os.execvp(sys.executable, [sys.executable] + sys.argv)
    import unittest
    # 寻找测试文件的目录tests
    tests = unittest.TestLoader().discover('tests')
    # 读取测试文件并运行测试
    unittest.TextTestRunner(verbosity=2).run(tests)
    if COV:
        COV.stop()
        COV.save()
        print('Coverage Summary:')
        COV.report()
        basedir = os.path.abspath(os.path.dirname(__file__))
        covdir = os.path.join(basedir, 'tmp/coverage')
        # 生成使用HTML编写的精美报告
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


@manager.command
def profile(length=25, profile_dir=None):
    # 在代码分析器下启动程序
    from werkzeug.contrib.profiler import ProfilerMiddleware
    app.wsgi_app = ProfilerMiddleware(app.wsgi_app, restrictions=[length],
                                      profile_dir=profile_dir)
    app.run()


@manager.command
def deploy():
    # 运行部署任务
    from flask_migrate import upgrade

    upgrade()  # 把数据库迁移到最新版本
    
    Role.insert_roles()  # 创建用户角色
    init()
    # 为新博客添加一些生气...
    fake.gen_fake_users(100)
    fake.gen_fake_blogs(300)
    fake.gen_follows(1000)
    fake.gen_fake_comments(1000)
    fake.gen_fake_tags()


def init():
    admin_role = Role.query.filter_by(name='Admin').first()
    mod_role = Role.query.filter_by(name='Moderator').first()
    u1 = User(email='208343741@qq.com',
              username='hikari星',
              password='aaa111',
              confirmed=True,
              name='hikari星',
              location='南京',
              about_me='python爱好者',
              role=mod_role,
              )
    u2 = User(email='2091248018@qq.com',
              username='hikari',
              password='aaa111',
              confirmed=True,
              name='hikari',
              location='南京',
              about_me='管理员大人',
              role=admin_role,
              )
    u1.image='/static/1411.png'
    u2.image='/static/maki.png'

    db.session.add_all([u1, u2])


if __name__ == '__main__':
    manager.run()
