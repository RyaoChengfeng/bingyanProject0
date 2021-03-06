# 功能：
# 爬取arvix论文的标题、序号、作者、时间、分类、下载链接
# 下载arivx论文
# 爬虫增量爬取
# 爬虫定时爬取
# 超时重试、跳过
# 实现代理（未使用）
# 实现多进程（本来使用协程，debug搞了3、4个小时、代码结构改了又改还未解决，故而放弃）


import re
import requests
import os
from bs4 import BeautifulSoup
import random
import pymysql

# from spiders import agent_ip


# 如果爬全部的论文就加上循环结构
years = ['20', '19', '18', '17', '16', '15', '14', '13', '12', '11', '10', '09', '08', '07', '06', '05', '04', '03',
         '02', '01', '00', '99', '98', '97', '96', '95', '94', '93']

# agent_url = 'http://www.66ip.cn/'

user_agent = [
    "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:38.0) Gecko/20100101 Firefox/38.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; .NET CLR 3.0.30729; .NET CLR 3.5.30729; InfoPath.3; rv:11.0) like Gecko",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)",
    "Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11",
    "Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)",
    "Mozilla/5.0 (iPhone; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPod; U; CPU iPhone OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (iPad; U; CPU OS 4_3_3 like Mac OS X; en-us) AppleWebKit/533.17.9 (KHTML, like Gecko) Version/5.0.2 Mobile/8J2 Safari/6533.18.5",
    "Mozilla/5.0 (Linux; U; Android 2.3.7; en-us; Nexus One Build/FRF91) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "MQQBrowser/26 Mozilla/5.0 (Linux; U; Android 2.3.7; zh-cn; MB200 Build/GRJ22; CyanogenMod-7) AppleWebKit/533.1 (KHTML, like Gecko) Version/4.0 Mobile Safari/533.1",
    "Opera/9.80 (Android 2.3.4; Linux; Opera Mobi/build-1107180945; U; en-GB) Presto/2.8.149 Version/11.10",
    "Mozilla/5.0 (Linux; U; Android 3.0; en-us; Xoom Build/HRI39) AppleWebKit/534.13 (KHTML, like Gecko) Version/4.0 Safari/534.13",
    "Mozilla/5.0 (BlackBerry; U; BlackBerry 9800; en) AppleWebKit/534.1+ (KHTML, like Gecko) Version/6.0.0.337 Mobile Safari/534.1+",
    "Mozilla/5.0 (hp-tablet; Linux; hpwOS/3.0.0; U; en-US) AppleWebKit/534.6 (KHTML, like Gecko) wOSBrowser/233.70 Safari/534.6 TouchPad/1.0",
    "Mozilla/5.0 (SymbianOS/9.4; Series60/5.0 NokiaN97-1/20.0.019; Profile/MIDP-2.1 Configuration/CLDC-1.1) AppleWebKit/525 (KHTML, like Gecko) BrowserNG/7.1.18124",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0; HTC; Titan)",
    "UCWEB7.0.2.37/28/999",
    "NOKIA5700/ UCWEB7.0.2.37/28/999",
    "Openwave/ UCWEB7.0.2.37/28/999",
    "Mozilla/4.0 (compatible; MSIE 6.0; ) Opera/UCWEB7.0.2.37/28/999",
    # iPhone 6：
    "Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25",

]

headers = {'User-Agent': random.choice(user_agent)}


# proxies = agent_ip.get_ip(agent_url, headers=headers)


# 获取每个论文代号
def get_number():
    # for year in years:
    year = '20'
    url_arvix0 = "https://arxiv.org/list/cs.AI/" + year
    page0 = requests.get(url_arvix0, headers=headers)
    html0 = page0.text
    print(html0)
    total0 = re.compile(r'total of (.*?) entries:')
    total = re.findall(total0, html0)[0]
    print(total)
    start = 0
    r_number_list = []
    for _ in range((int(total) // 2000) + 1):  # 爬取该年份的所有论文
        url_arvix = "https://arxiv.org/list/cs.AI/" + year + "?skip=" + str(start) + "&show=2000"
        start += 2000
        page = requests.get(url_arvix, headers=headers)
        html = page.text
        r_number = re.compile(r'<a href="/abs/(.*?)" title="Abstract">')
        r_number_list0 = re.findall(r_number, html)
        r_number_list += r_number_list0
        print(r_number_list)
    return r_number_list


# 进入论文内部爬取
# ps:表示首页不会显示时间信息，要爬就要进论文里面。但这样一来花的时间就大大增加了.
def get_msg(number):
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='liaocfe',
        port=3306,
        db='bingyanProject0',
    )
    cursor = db.cursor()
    # 论文序号
    number_id = 'arXiv:' + number
    i = compare_url(number_id)
    if i:
        print('论文 arXiv:' + number + '已存在')
        return None
    else:
        url_doc = 'https://arxiv.org/abs/' + number
        # 超时重试3次
        i = 0
        while i < 3:
            try:
                doc = requests.get(url_doc, headers=headers, timeout=5)  # 设置超时
            except requests.exceptions.RequestException as e:
                i += 1
                print('重试 %s' % url_doc)
            else:
                doc = doc.text
                break

        if i == 3:
            print(print('%s 访问失败！' % url_doc))
            print(e)
            return None

        # 信息提示
        print('正在爬取论文: %s' % number_id)

        soup = BeautifulSoup(doc, 'lxml')
        # 获得论文信息

        # 论文标题
        r_title0 = re.compile(r'<h1 class="title mathjax"><span class="descriptor">Title:</span>(.*?)</h1>')
        r_title = re.findall(r_title0, doc)[0]
        # 论文作者
        div = soup.find_all(attrs={'class': 'authors'})[0]
        author_list = div.find_all(name='a')
        authors = ''
        for author in author_list:
            author = author.string
            i = True
            while i:  # 防止有的人名字有两个单引号，故而用循环
                if "'" in author:
                    author = author.replace("'", "''")  # 防止作者名字中有单引号
                else:
                    i = False
            if author == author_list[0].string:
                authors = author
            else:
                authors = authors + ',' + author
        if authors[0] == ',':  # 由于把单引号变成双引号后作者名字发生了改变
            authors = authors[1:]

        # 论文时间(之前读入数据库时的部分时间，由于正则没写好，所有多次提交的论文时间都出现了信息冗余)
        r_time0 = re.compile(r'Submitted on ([ A-Za-z0-9]*)')
        r_time = re.findall(r_time0, doc)[0]
        # 论文类别
        sbj = soup.find_all('span', class_='primary-subject')[0]
        sbj = str(sbj.string)
        # 下载地址
        url_pdf = "https://arxiv.org/pdf/" + number + '.pdf'

        # 插入数据库
        sql = "INSERT INTO documents(title,number,author,time,subject,url_pdf) VALUES('" + \
              r_title + "','" + number_id + "','" + authors + "','" + r_time + "','" + sbj + "','" + url_pdf + "');"  # 处理单引号
        try:
            cursor.execute(sql)
            db.commit()
            print("数据写入成功")
        except Exception as e:
            print('数据写入失败!', e)
            db.rollback()


# 下载功能
def download_all_pdf(url, number):
    pdf_file = requests.get(url, headers=headers, stream=True)
    # stream=True保持流的开启,直到流的关闭
    file_dir = '../Artificial Intelligence'
    pdf_name = number + '.pdf'
    if not os.path.exists(file_dir):
        os.makedirs(file_dir)
    fileroute = os.path.join(file_dir, pdf_name)
    with open(fileroute, 'wb') as f:
        for chunk in pdf_file.iter_content(chunk_size=1024):
            if chunk:
                f.write(chunk)


# 下载各论文到Artificial Intelligence
def get_all_doc(number):
    url_pdf = "https://arxiv.org/pdf/" + number + '.pdf'
    print('开始下载论文：arXiv:%s' % number)
    download_all_pdf(url_pdf, number)


# 判断url是否之前被爬取过
# 观察到无论上传几次，论文id都不会变，所以没必要用哈希来解析内容
def compare_url(number_id):
    sql = "SELECT number FROM documents WHERE number='" + number_id + "'"
    db = pymysql.connect(
        host='localhost',
        user='root',
        password='liaocfe',
        port=3306,
        db='bingyanProject0',
    )
    cursor = db.cursor()
    cursor.execute(sql)
    result = cursor.fetchone()
    return result
