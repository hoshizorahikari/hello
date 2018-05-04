from threading import Thread
from flask import current_app, render_template
from flask_mail import Message
from . import mail  # __init__.py中的mail对象
# 异步发送邮件


def send_async_mail(app, msg):
    with app.app_context():
        mail.send(msg)


def send_mail(to, subject, template, **kwargs):
    # to为接收方,subject为邮件主题,template为渲染邮件正文的模板
    app = current_app._get_current_object()  # 将app传给子线程?
    msg = Message(subject, sender=app.config['FLASKY_MAIL_SENDER'], recipients=[to])
    msg.body = render_template(template + '.txt', **kwargs)
    msg.html = render_template(template + '.html', **kwargs)

    t = Thread(target=send_async_mail, args=[app, msg])
    t.start()
    return t
