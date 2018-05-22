from random import randint
from sqlalchemy.exc import IntegrityError
from faker import Faker
from . import db
from .models import User, Blog, Follow, Comment, Role


def gen_fake_users(count=100):
    # 默认生成100个虚拟小伙伴

    fake = Faker('zh_CN')  # 支持中文
    i = 0
    while i < count:
        email = fake.email()
        u = User(email=email,
                 username=fake.user_name(),
                 password='aaa111',
                 #  password='{}{}'.format(email.split(
                 #      '@')[0], (127*i**3+53*i**2+23*i+97) % 10000),
                 confirmed=True,
                 name=fake.name(),
                 location=fake.city(),
                 about_me='我是机器人',
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
        c = Comment
        b = Blog(body=fake.text(200),
                 timestamp=fake.past_date(),
                 author=u,
                 title=fake.text(20))

        db.session.add(b)
    db.session.commit()


def gen_follows(count=100):
    # 随机分配关注
    user_count = User.query.count()
    hikari = User.query.filter_by(username='hikari').first()

    if hikari:
        for j in range(user_count):
            u = User.query.offset(j).first()
            if u != hikari:
                u.follow(hikari)
    i = 0
    while i < count:
        # offset()过滤器跳过指定记录数量; 通过设置随机偏移,
        # 再调用first()相当于每次随机选一个用户
        u1 = User.query.offset(randint(0, user_count - 1)).first()
        u2 = User.query.offset(randint(0, user_count - 1)).first()
        if u1 == u2 or u1.is_following(u2) or u1 == hikari:
            continue
        u1.follow(u2)
        i += 1
    db.session.commit()


def gen_fake_comments(count=100):
    # 为count篇文章分配评论
    fake = Faker('zh_CN')
    user_count = User.query.count()
    blog_count = Blog.query.count()
    for i in range(count):
        # offset()过滤器跳过指定记录数量; 通过设置随机偏移,
        # 再调用first()相当于每次随机选一个用户
        u = User.query.offset(randint(0, user_count - 1)).first()
        b = Blog.query.offset(randint(0, blog_count - 1)).first()
        # b = Blog.query.first()
        c = Comment(body=fake.text(100),
                    timestamp=fake.past_date(),
                    author=u,
                    blog=b)

        db.session.add(c)
    db.session.commit()
