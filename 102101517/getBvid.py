import re

temp_filename = "pagejson/page{i}.txt"
file_prefix = "file"
file_count = 8
for i in range(1,file_count+1):
    filename = temp_filename.replace("{i}",str(i))
    file = open(filename, 'r', encoding='utf-8')
    content = file.readline()
    # 利用正则表达式从json文本中获取页面视频的bvid
    bvid = re.findall('\"bvid\":\"(.*?)\"', content)
    # 将re.findall匹配结果写入文件便于后续处理
    for index in bvid:
        with open('bvid.txt', mode='a', encoding='utf-8') as file:
            file.write(index)
            file.write('\n')
            # 打印提取数据
            print(bvid)




