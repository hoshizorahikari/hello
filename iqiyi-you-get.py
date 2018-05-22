import os
import requests
from bs4 import BeautifulSoup as BS
import re
import time


class iQiYi():
    # use you-get
    def __init__(self, url):
        self.url = url
        self.headers = {'User-Agent':
                        'Mozilla/5.0 (xyzdows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2785.104 Safari/537.36 Core/1.53.3211.400 QQBrowser/9.6.11523.400',
                        }
        self.path = 'D:/hikari星/iqiyi/'

    def get_html(self, url):
        while True:
            try:
                res = requests.get(url, headers=self.headers)
            except:
                time.sleep(1)
            else:
                return res.text

    def parse(self):
        html = self.get_html(self.url)
        soup = BS(html, 'lxml')
        self.title = soup.select('.main_title')[0].a.text
        print(self.title)

        div = soup.select('.wrapper-piclist')[0]
        lst = div.select('.site-piclist_info_title')
        i = 0
        self.dct = {}
        while i < len(lst)-1 or i < len(lst):
            url = lst[i].a['href']
            pre = lst[i].text.strip()
            title = lst[i+1].text.strip()
            dct = {'?': '？', ':': ' ', '"': ''}
            for k, v in dct.items():
                if k in title:
                    title = title.replace(k, v)
            p = r'第(\d+)集'
            l = re.findall(p, pre)
            if len(l) != 1:
                return
            n = int(l[0])
            title = '{:02d} {}.mp4'.format(n, title)
            old = '{}{}.mp4'.format(self.title, pre)
            print(old)
            self.dct[title] = (url, old)

            i += 2

    def download(self):
        self.parse()
        path = os.path.join(self.path, self.title)
        if not os.path.exists(path):
            os.mkdir(self.title)
        os.chdir(path)
        lst = os.listdir(path)
        for title, tup in self.dct.items():
            if title in lst:
                print('{}已经存在！'.format(title))
                continue
            cmd = 'you-get {}'.format(tup[0])
            os.system(cmd)
            time.sleep(1)
            os.rename(tup[1], title)

    def __call__(self):
        self.download()


if __name__ == '__main__':
    urls = [
        'http://www.iqiyi.com/a_19rrh05ogd.html',  # 偶活学园Friends!
        'http://www.iqiyi.com/a_19rrh05oat.html',  # 最后的休止符
        'http://www.iqiyi.com/a_19rrgyjath.html',  # 三次元女友
        'http://www.iqiyi.com/a_19rrh1qb8l.html',  # 齐木楠雄的灾难 第2季
        'http://www.iqiyi.com/a_19rrhek9x9.html',  # 黑色四叶草
        'http://www.iqiyi.com/a_19rrh0gytx.html',  # 妖怪旅馆营业中
        'http://www.iqiyi.com/a_19rrh0tfud.html',  # 拥抱！光之美少女
        'http://www.iqiyi.com/a_19rrgymz6t.html',  # 美妙频道
        'http://www.iqiyi.com/a_19rrhcangd.html',  # 阿松2
        'http://www.iqiyi.com/a_19rrh0z2qt.html',  # 怪兽娘～奥特怪兽拟人化计划～ 第2季
        'http://www.iqiyi.com/a_19rrhbcjih.html',  # 数码宝贝tri.
    ]
    for i in urls:
        iqiyi = iQiYi(i)
        iqiyi()
