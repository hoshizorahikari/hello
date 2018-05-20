import os
import re
import requests
import time
from bs4 import BeautifulSoup as BS
import sys


class YOUKU():
    def __init__(self, m3u8):
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (xyzdows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3211.400 QQBrowser/9.6.11523.400',
                        'Referer': 'http://www.youku.com/'}
        self.path = 'E:/迅雷下载/'
        self.m3u8 = m3u8
        self.video = []
        self.name = 'output'
        self.get_lst()

    def get_lst(self):
        html = self.get_m3u8()
        lst = [x.split('&ts_start')[0] for x in html.split() if 'http' in x]
        time.sleep(1)
        self.video = [(url.split('?ccode')[0].split('/')[-1], url)
                      for url in list(set(lst))]
        if len(self.video) == 0:
            return
        tmp = set([x[12:50] for x, y in self.video])
        if len(tmp) > 1:
            dct = {}
            for i in tmp:
                for x, y in self.video:
                    if i in x:
                        if i not in dct.keys():
                            dct[i] = 1
                        else:
                            dct[i] += 1

            lst = list(dct.items())
            lst.sort(key=lambda x: x[1])
            sub = lst[-1][0]  # 取最多的
            self.video = [(x, y) for x, y in self.video if sub in x]
        self.video.sort(key=lambda x: x[0])
        # print(self.video)
        self.can_youku()

    def can_youku(self):
        """判断视频是否连续"""
        if len(self.video) < 4:
            self.video = []
            return
        i = self.get_start_diff_num(self.video[0][0], self.video[1][0])
        num = [int(x[i - 1:i + 1], 16) for x, y in self.video]  # 16进制转为10进制
        for n in num:
            if n != num.index(n):  # 判断是否连续
                self.video = []

    def get_start_diff_num(self, a, b):
        """字符串a,b第几个开始不同"""
        for i in range(min(len(a), len(b))):
            if a[i] != b[i]:
                return i

    def download(self):
        BUFF_SIZE = 1024 * 1024 * 2
        cnt, size = 0, len(self.video)
        os.chdir(self.path)
        if os.path.exists('{}.mp4'.format(self.name)):
            raise BaseException('{}.mp4已经存在'.format(self.name))

        for file, url in self.video:
            cnt += 1

            if os.path.exists(file):
                print('{}已经存在！'.format(file))
                continue
            time.sleep(0.3)
            print('正在下载第{}/{}个文件'.format(cnt, size))
            start = time.time()
            while True:
                try:
                    # res = requests.get(url, headers=self.headers)
                    res = requests.get(url, headers=self.headers, stream=True)
                except:
                    time.sleep(2)
                else:
                    with open(file, 'wb') as f:
                        # f.write(res.content)
                        for chunk in res.iter_content(chunk_size=BUFF_SIZE):
                            if chunk:
                                f.write(chunk)
                    end = time.time()
                    t = end - start
                    if t < 60:
                        print('下载完成！用时{:.2f}秒'.format(t))
                    else:
                        minute = int(t // 60)
                        second = int(t % 60 + 0.5)
                        print('下载完成！用时{}分{}秒'.format(minute, second))

                    break

    def merge(self):
        os.chdir(self.path)
        filelst = ["file '{}'".format(x) for x, y in self.video]
        txt = '{}.txt'.format(self.name)
        with open(txt, 'w') as f:
            f.write('\n'.join(filelst))
            # for i in filelst:
            # f.writelines(i + '\n')
        cmd = 'ffmpeg -f concat -i "{}" -vcodec copy -acodec copy "{}.mp4"'.format(
            txt, self.name)
        os.system(cmd)
        time.sleep(1)
        for i, j in self.video:
            os.remove(i)
        os.remove(txt)

    def start(self):
        try:
            self.download()
        except BaseException as e:
            print(e)
        else:
            print('下载完成，准备合并！')
            time.sleep(1)
            self.merge()
            print('合并完成！')

    def __call__(self, *args, **kwargs):

        if self.video:
            self.start()
        else:
            print('No video to download!!')

    def get_m3u8(self):
        vid = self.m3u8.split('vid=')[-1].split('&')[0]
        url = 'http://v.youku.com/v_show/id_{}.html'.format(
            vid.replace('%3D', '='))
        while True:
            try:
                html = requests.get(url, headers=self.headers).text
                p = r'<title>(.+?)—在线播放—《(.+?)》'
                lst = re.findall(p, html)
                self.name = lst[0][0]
                if self.name.startswith('第'):
                    d = lst[0][1]
                    os.chdir(self.path)
                    for i in os.listdir(self.path):
                        if os.path.isdir(i) and d in i:
                            d = i
                            break
                    else:
                        os.mkdir(d)
                    self.path = os.path.join(self.path, d)

            except Exception as e:
                print('{} 发生错误\n\t{}'.format(url, e))
                time.sleep(1)
            else:
                break

        print(self.name.center(50, '*'))
        dct = {'?': '？', ':': ' ', '"': ''}
        for k, v in dct.items():
            if k in self.name:
                self.name = self.name.replace(k, v)
        time.sleep(1)
        self.headers['Referer'] = url
        html = requests.get(self.m3u8, headers=self.headers).text
        return html


if __name__ == '__main__':
    if len(sys.argv) < 2:
        sys.exit('python youku-m3u8.py m3u8_url')
    m3u8 = sys.argv[1]
    youku = YOUKU(m3u8)
    youku()
