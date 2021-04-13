# -*- coding: utf-8 -*-
import os
from multiprocessing import Pool

import requests
from retrying import retry

# 开始帧
BEGIN = 0
# 结束帧
END = 20
L = 3
# TS文件url
URL = "https://woku.fofoxi.com/s03/b/2/8/ff213fdab0627359e8f7fe058cc3f/hls/h264/"
# TS文件存放位置
TS_FILE = "/Users/ls/Downloads/ts/"
# 合并后文件存放位置
MP4_FILE = "/Users/ls/Downloads/"
# 视频名
NAME = "test.mp4"


def TsDirInit():
    if not os.path.exists(TS_FILE):
        os.makedirs(TS_FILE)
    else:
        os.system("rm -r {}*.ts".format(TS_FILE))
        os.system("rm -r {}*.txt".format(TS_FILE))
    if not os.path.exists(MP4_FILE):
        os.makedirs(TS_FILE)


class Tentacle(object):
    def __init__(self):
        self._headers = {
            "Connection": "keep-alive",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6)"
                          " AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36"}

    @retry(stop_max_attempt_number=10)
    def download(self, URL, _tsFileNumber):
        url = "{}{}.ts".format(URL, _tsFileNumber)
        r = requests.get(url, headers=self._headers, timeout=5)
        try:
            if r.status_code != 200:
                print("Requests Failed Code:{},Msg:{}".format(r.status_code, r.text))
                return
            print("{}.ts DownLoading...".format(_tsFileNumber))
            with open("{}{}.ts".format(TS_FILE, _tsFileNumber), "wb") as f:
                f.write(r.content)
            print("{}.ts DownLoad Over...".format(_tsFileNumber))
        except Exception as e:
            print(e)


class Ffmpeg(object):
    def __init__(self):
        self._mergeCmd = ""
        self._buildTsFileListCmd = ""

    def SetCmd(self, mergeCmd):
        self._mergeCmd = mergeCmd

    def buildTsFileList(self, localTsFileList):
        with open("{}file_list.txt".format(TS_FILE), "w+") as f:
            for file in localTsFileList:
                f.write("file '{}'\n".format(file))

    def merageTsFiletoMp4(self):
        os.system(self._mergeCmd)


if __name__ == '__main__':
    print("Start init dir")
    TsDirInit()
    print("Over init...")
    dueTsfileNumber = []
    tec = Tentacle()
    dueTsfileNumber = range(BEGIN, END)
    tsFileNumList = []

    # 复验下载文件是否完整
    print("Check File...")
    tsFileNumLackList = set(dueTsfileNumber) - set(tsFileNumList)  # 应下载Ts文件ID跟本地实际下载文件ID比对得出缺少的Ts文件再次进行下一轮下载
    while tsFileNumLackList:
        print("Total:{} Need Re Download...".format(len(tsFileNumLackList)))
        po = Pool(100)
        for num in tsFileNumLackList:
            distance = L - len(str(num))
            tsFileNumber = "{}{}".format("0" * distance, num) if distance != 0 else num
            po.apply_async(tec.download, args=(URL, tsFileNumber))
        po.close()
        po.join()
        tsFileList = sorted(os.listdir(TS_FILE))
        tsFileNumList = [int(ts.split('.')[0]) for ts in tsFileList]
        tsFileNumLackList = list(set(dueTsfileNumber) - set(tsFileNumList))

    # # 生成ffmpeg所需文件目录
    print("Build File Dir...")
    ffmpeg = Ffmpeg()
    ffmpeg.SetCmd("ffmpeg -f concat -i {}file_list.txt -c copy {}{}.mp4".format(TS_FILE, MP4_FILE, NAME))
    ffmpeg.buildTsFileList(tsFileList)

    print("Merge Files...")
    ffmpeg.merageTsFiletoMp4()
    print("Download Success")
