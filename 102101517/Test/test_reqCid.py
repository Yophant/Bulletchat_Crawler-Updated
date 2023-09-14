
import requests
import re
import queue
import threading

import unittest


class TestCvid(unittest.TestCase):
    def test_get_cvid(self):

        bvid_queue = queue.Queue()
        video_number = 300

        # 将bvid依次放入队列中，方便后续多线程和锁的配合使用
        with open('bvid.txt', 'r') as file:
            for i, line in enumerate(file, 1):
                if i <= video_number:
                    bvid_queue.put(line.strip())
        # 线程类封装
        threadLock = threading.Lock()

        class myThread(threading.Thread):
            def __init__(self, threadId):
                threading.Thread.__init__(self)
                self.threadId = threadId

            def run(self):
                print('开始线程'), self.name
                req_Cid()

        def req_Cid():
            try:
                temp_url = "https://www.ibilibili.com/video/{bvid}"
                with open('bvid.txt', 'r') as file:
                    while not bvid_queue.empty():
                        # 把bvid套进链接格式中得出视频URL
                        url = temp_url.replace("{bvid}", bvid_queue.get())
                        # 通过URL请求html文本内容
                        response = requests.get(url)
                        response.encoding = 'utf-8'
                        # <Response [200]> response对象 200状态码 表示请求成功
                        if response.status_code == 200:
                            # 再通过正则表达式得到弹幕api
                            bulletchat_api = re.findall(
                                'value=\"(https://api\.bilibili\.com/x/v1/dm/list\.so\?oid=.*?)\" class',
                                response.text)
                            for index in bulletchat_api:
                                threadLock.acquire()
                                with open('cid.txt', mode='a', encoding='utf-8') as f:
                                    f.write(index)
                                    f.write('\n')
                                    print(index)
                                    threadLock.release()
                        else:
                            print('请求失败,状态码：', response.status_code)
            except (ConnectionError, IndexError, AttributeError, requests.RequestException) as e:
                print(f"获取cid出现异常: {e}")
                return None

        # 线程对象数组创建
        threads = []
        thread_Array = [myThread(i) for i in range(16)]
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