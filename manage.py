import os
from app import create_app, db
from app.models import User, Role, Permission, Blog, Comment
from flask_script import Manager, Shell
from flask_migrate import Migrate, MigrateCommand
import app.fake as fake

app = create_app(os.getenv('FLASK_CONFIG') or 'default')

# app_context = app.app_context()  # 激活上下文
# app_context.push()
# db.create_all()  # 创建数据库

manager = Manager(app)
migrate = Migrate(app, db)


def make_shell_context():
    return dict(app=app, db=db, User=User, Role=Role, Permission=Permission, Blog=Blog, fake=fake, Comment=Comment)


manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command('db', MigrateCommand)


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    unittest.TextTestRunner(verbosity=2).run(tests)


# @app.shell_context_processor
# def make_shell_context():
#     return dict(db=db, User=User, Role=Role)


# @app.cli.command()
# def test():
#     """Run the unit tests."""
#     import unittest
#     tests = unittest.TestLoader().discover('tests')
#     unittest.TextTestRunner(verbosity=2).run(tests)

if __name__ == '__main__':

    manager.run()
