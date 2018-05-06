import os
import re
import requests
import time
from bs4 import BeautifulSoup as BS
import sys
from threading import Thread, Lock


class QQNBA():
    def __init__(self, m3u8):
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (xyzdows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3211.400 QQBrowser/9.6.11523.400'}
        self.path = os.path.abspath('.')
        self.m3u8 = m3u8
        #self.video = []
        self.name = 'output'
        self.lock = Lock()
        self.total_thread = 50
        self.thread_lst = []
        self.video = self.ts_generator()

    def get_m3u8(self):
        while True:
            try:
                html = requests.get(self.m3u8, headers=self.headers).text
            except:
                time.sleep(1)
            else:
                return html

    def ts_generator(self):
        html = self.get_m3u8()
        a = self.m3u8.rfind('/')
        pre = self.m3u8[:a]
        self.name = self.m3u8[a+1:].split('.ts.m3u8')[0]
        self.lst = []
        for i in html.split():
            if '.ts' in i:
                url = '{}/{}'.format(pre, i)
                file = i.split('?index')[0]
                self.lst.append(file)
                yield (url, file)

        #lst = [x for x in html.split() if '.ts' in x]
        #self.video=[('{}/{}'.format(pre,x),x.split('?index')[0]) for x in lst]

    def download(self, file, url, thread_name):
        """下载"""
        # 无限请求直到请求成功，失败睡一会
        while True:
            try:
                res = requests.get(url, headers=self.headers)
            except:
                print('连不上，我要睡觉！')
                time.sleep(1)
            else:
                with open(file, 'wb') as f:
                    f.write(res.content)
                print('{}：{}下载完成！'.format(thread_name, file))
                break

    def merge(self):
        """合并分段视频"""
        os.chdir(self.path)
        filelst = ["file '{}'".format(x) for x in self.lst]
        txt = '{}.txt'.format(self.name)
        with open(txt, 'w') as f:
            f.write('\n'.join(filelst))

        cmd = 'ffmpeg -f concat -i "{}" -vcodec copy -acodec copy "{}.mp4"'.format(
            txt, self.name)
        os.system(cmd)
        time.sleep(1)
        for i in self.lst:
            os.remove(i)
        os.remove(txt)

    def run(self, thread_name):
        """多线程执行任务，提取生成器内容，下载"""
        while True:
            try:  # 获取生成器下一个，直到没货
                with self.lock:  # 需要互斥锁
                    url, file = next(self.video)
            except:  # 没货就结束
                break
            if os.path.exists(file):
                print('{}已经存在！'.format(file))
            else:
                self.download(file, url, thread_name)
        print('{} over'.format(thread_name))
        self.total_thread -= 1
        print('剩余{}个线程'.format(self.total_thread))

    def __call__(self, *args, **kwargs):
        os.chdir(self.path)
        if os.path.exists('{}.mp4'.format(self.name)):
            raise BaseException('{}.mp4已经存在！'.format(self.name))
        for i in range(self.total_thread):
            thread_name = '线程--{:02d}--'.format(i + 1)
            t = Thread(target=self.run, args=(thread_name,))
            t.start()
            self.thread_lst.append(t)
        # 主线程等待子线程结束
        for t in self.thread_lst:
            t.join()
        print('下载完成，准备合并！')
        time.sleep(1)
        self.merge()
        print('合并完成！')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('python tencent-m3u8.py m3u8_url')
    m3u8 = sys.argv[1]
    QQNBA(m3u8)()
