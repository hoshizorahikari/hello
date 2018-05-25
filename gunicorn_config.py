from gevent import monkey
monkey.patch_all()

import multiprocessing
debug = True
loglevel = 'debug'
bind = '127.0.0.1:5000'
pidfile = 'log/gunicorn.pid'  # 需要手动创建log目录, 否则报错
logfile = 'log/debug.log'

workers = multiprocessing.cpu_count() * 2 + 1
worker_class = 'gevent'  # gunicorn默认阻塞,选择gevent模式。
