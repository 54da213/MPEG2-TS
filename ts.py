# -*- coding: utf-8 -*-
import os
import time
import requests
from retrying import retry
from multiprocessing import Pool
# 开始帧
BEGIN = 0
# 结束帧
END = 616
L = 3
# TS文件url
URL = "https://youku.com-movie-youku.com/20190123/8498_1da49ddf/1000k/hls/c854d89a6e2"
TS_FILE = "/Users/ls/Downloads/ts/"
MP4_FILE = "/Users/ls/Downloads/"
LINK_FILE = "./"
# 视频名
NAME = "古董局中局31"


def to_num(_str):
    p = 0
    l = len(_str)
    while p < l:
        if _str[p] != "0":
            break
        if p == 2:
            return "0"
        p += 1
    return _str[p:]


@retry(stop_max_attempt_number=10)
def download(url, n):
    headers = {
        "Connection": "keep-alive",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)"
                      " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}
    r = requests.get(url, headers=headers, timeout=5)
    try:
        if r.status_code != 200:
            print("Requests Failed Code:{},Msg:{}".format(r.status_code, r.text))
            return
        print("{}.ts DownLoading...".format(n))
        with open("{}{}.ts".format(TS_FILE, n), "wb") as f:
            f.write(r.content)
        print("{}.ts DownLoad Over...".format(n))
    except Exception as e:
        print(e)


if __name__ == '__main__':
    print("----------Init Mid File...-------------")
    fps = []
    os.system("rm -r {}*.ts".format(TS_FILE))
    os.system("rm -r {}*.txt".format(TS_FILE))
    time.sleep(1)
    po = Pool(100)
    for i in range(BEGIN, END):
        fps.append(i)
        distance = L - len(str(i))
        n = "{}{}".format("0" * distance, i) if distance != 0 else i
        url = "{}{}.ts".format(URL, n)
        po.apply_async(download, args=(url, n))
    po.close()
    po.join()
    print("Over File DownLoad...")

    time.sleep(1)
    file_list = sorted(os.listdir(TS_FILE))[1:]
    ts_group = []
    for file in file_list:
        ts_group.append(int(to_num(file.split(".")[0])))

    # 复验下载文件是否完整
    print("--------------Check File...------------------")
    fill_group = list(set(fps) - set(ts_group))
    while fill_group:
        print("-----Total{}Need to be supplemented------".format(len(fill_group)))
        po = Pool(100)
        for j in fill_group:
            distance = L - len(str(j))
            n = "{}{}".format("0" * distance, j) if distance != 0 else j
            url = "{}{}.ts".format(URL, n)
            po.apply_async(download, args=(url, n))
        po.close()
        po.join()
        file_list = sorted(os.listdir(TS_FILE))[1:]
        for file in file_list:
            ts_group.append(int(to_num(file.split(".")[0])))
        fill_group = list(set(fps) - set(ts_group))
    # 生成ffmpeg所需文件目录
    print("----------------Build File List...-----------------")
    with open("{}file_list.txt".format(TS_FILE), "w+") as f:
        for file in file_list:
            f.write("file '{}'\n".format(file))

    print("----------------Merge Files...-----------------")
    os.system("ffmpeg -f concat -i {}file_list.txt -c copy {}{}.mp4".format(TS_FILE, MP4_FILE, NAME))
    print("----------Download Success---------")
