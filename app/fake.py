from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Blog


def gen_fake_users(count=100):
    # 默认生成100个虚拟小伙伴
    fake = Faker('zh_CN')  # 支持中文
    i = 0
    while i < count:
        u = User(email=fake.email(),
                 username=fake.user_name(),
                 password='password',
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me=fake.text(),
                 member_since=fake.past_date())
        db.session.add(u)
        # 随着数据增加会有重复的风险,提交时会抛出IntegrityError异常,需要回滚会话
        try:
            db.session.commit()
            i += 1
        except IntegrityError:
            db.session.rollback()


def gen_fake_blogs(count=100):
    # 为count篇文章分配作者
    fake = Faker('zh_CN')
    user_count = User.query.count()
    for i in range(count):
        # offset()过滤器跳过指定记录数量; 通过设置随机偏移,
        # 再调用first()相当于每次随机选一个用户
        u = User.query.offset(randint(0, user_count - 1)).first()
        p = Blog(body=fake.text(),
                 timestamp=fake.past_date(),
                 author=u)
        db.session.add(p)
    db.session.commit()
