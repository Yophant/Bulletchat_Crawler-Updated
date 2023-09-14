import re
import requests
import random
import threading
import time
import datetime
import queue
import pandas as pd
import heartrate

# 程序执行次数可视化分析
# heartrate.trace(browser=True)

start = '20230101'
end = '20230906'
date = [x for x in pd.date_range(start, end).strftime('%Y-%m-%d')]


user_agent = [
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.1 (KHTML, like Gecko) Chrome/22.0.1207.1 Safari/537.1",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1092.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.6 (KHTML, like Gecko) Chrome/20.0.1090.0 Safari/536.6",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/117.0",
    "Mozilla/5.0 (Windows NT 6.0) AppleWebKit/536.5 (KHTML, like Gecko) Chrome/19.0.1084.36 Safari/536.5",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1063.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1062.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.1 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2) AppleWebKit/536.3 (KHTML, like Gecko) Chrome/19.0.1061.0 Safari/536.3",
    "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/535.24 (KHTML, like Gecko) Chrome/19.0.1055.1 Safari/535.24"
]
start_time = datetime.datetime.now()
headers = {
    "origin": "https://www.bilibili.com",
    "cookie": "_uuid=0EBFC9C8-19C3-66CC-4C2B-6A5D8003261093748infoc; buvid3=4169BA78-DEBD-44E2-9780-B790212CCE76155837infoc; sid=ae7q4ujj; DedeUserID=501048197; DedeUserID__ckMd5=1d04317f8f8f1021; SESSDATA=e05321c1%2C1607514515%2C52633*61; bili_jct=98edef7bf9e5f2af6fb39b7f5140474a; CURRENT_FNVAL=16; rpdid=|(JJmlY|YukR0J'ulmumY~u~m; LIVE_BUVID=AUTO4315952457375679; CURRENT_QUALITY=80; bp_video_offset_501048197=417696779406748720; bp_t_offset_501048197=417696779406748720; PVID=2",
    "user-agent": random.choice(user_agent),
}
params = {
    'type': 1,
    'oid': '1245291456',
    'date': date
}
#将弹幕api放入queue中，方便后续多线程和锁的控制
url_queue = queue.Queue()
with open('cid.txt', 'r') as file:
    for i, line in enumerate(file, 1):
        url_queue.put(line.strip())

threadLock = threading.Lock()
class myThread(threading.Thread):
    def __init__(self,threadId):
        threading.Thread.__init__(self)
        self.threadId = threadId
    def run(self):
        print('开始线程'),self.name
        Get_Bulletchat()

def Get_Bulletchat():
    try:
        with open('cid.txt','r') as file:
            while not url_queue.empty():
                # 通过弹幕api请求弹幕网页内容
                response = requests.get(url=url_queue.get(),json=params,headers=headers)
                response.encoding = response.apparent_encoding
                # <Response [200]> response对象 200状态码 表示请求成功
                if response.status_code == 200:
                    # 通过正则表达式提取弹幕内容
                    data_list = re.findall('<d p=".*?">(.*?)</d>', response.text)
                    for index in data_list:
                        #开启锁
                        threadLock.acquire()
                        with open('bulletchat.txt', mode='a', encoding='utf-8') as f:
                            f.write(index)
                            f.write('\n')
                            print(index)
                            #释放锁
                            threadLock.release()
                    # 休眠,减少因连续请求导致ip封锁的风险
                    time.sleep(random.randint(1, 2))
                else:
                    print('请求失败,状态码：',response.status_code)
    except (ConnectionError, IndexError, AttributeError, requests.RequestException) as e:
        print(f"获取弹幕出现异常: {e}")
        return None

threads = []
thread_Array=[myThread(i) for i in range(16)]
# 创建16个线程
for i in range(16):
    thread_Array[i] = myThread(i)
for i in range(16):
    # 添加线程到线程列表
    threads.append(thread_Array[i])
    # 开启新线程
    thread_Array[i].start()

# 等待所有线程完成
for t in threads:
    t.join()
print('主进程结束')