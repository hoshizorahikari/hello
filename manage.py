import os

COV = None
if os.environ.get('FLASK_COVERAGE'):
    import coverage
    COV = coverage.coverage(branch=True, include='app/*')
    COV.start()

from flask_migrate import Migrate, MigrateCommand
from app import create_app, db
from app.models import User, Role, Permission, Blog, Comment, Follow
import app.fake as fake
from flask_script import Manager, Shell


app = create_app(os.getenv('FLASK_CONFIG') or 'default')

app_context = app.app_context()  # 激活上下文
app_context.push()
db.create_all()  # 创建数据库

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Blog=Blog, fake=fake, Comment=Comment)


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
    """单元测试"""
    if coverage and not os.environ.get('FLASK_COVERAGE'):
        import sys
        os.environ['FLASK_COVERAGE'] = '1'
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
        COV.html_report(directory=covdir)
        print('HTML version: file://{}/index.html'.format(covdir))
        COV.erase()


@manager.command
def init():
    from flask_migrate import upgrade
    upgrade()
    Role.insert_roles()
    fake.gen_fake_users(100)
    fake.gen_fake_blogs(1000)
    fake.gen_follows(1000)
    fake.gen_fake_comments(400)


if __name__ == '__main__':
    manager.run()
