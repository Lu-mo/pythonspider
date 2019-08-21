#83
#137
from aiohttp_requests import requests
import asyncio
import os
import shutil
import aiohttp
import aiofiles
import time
#print("downloading with requests")
async def downloadM3u8(path,fileName,url):
    #url = 'https://radioluntan.space/apiv286.m3u8?request=3DTXnd8fqSVbdQSsymV8NTV5y16yduUkMOnguZBOCoH6YuKRk4tFLsJp%2BIheovJ8mDgYyvZq0j2U9GlP7hXaYYZ9dxtknVg0glSFsx4m58V%2FBsdYDvIrrKwGdQBZB9qHKG5y6feBrDrS27eUtWqpJXd%2BbFoMo0mfBfJen2ljBEJh5zT8bl3hvXxhxMvOilo3b1YB1f%2B0GpZUwhHKdpD1U4apoKnHGvtNB6RTOVDgBvhyRPPKBBSoS%2FD8lqUPndDDsgdG7uaqQC7EyLH5jDBMk79oU8ua7CYGsVf0NqIc1Hx0hAMTInQWyFuOFDHgHgWq%2Fm5C5TnxfXp8I1RMx4YQmxddmzT4LJTmWv5458DsIVE%3D'
    r = await requests.get(url)
    async with aiofiles.open(path + fileName + ".m3u8", "wb") as code:
        await code.write(await r.read())
        await code.flush()


async def download(filePath,download_path):
    #download_path = "D:\\m3u8\\download"#os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    #all_content = requests.get(filePath).text# 获取M3U8的文件内容
    #file_line = all_content.split("\r\n")  # 读取文件里的每一行
    file_line = list()
    async with aiofiles.open(filePath, "r", encoding="utf-8") as f:
        all_content = await f.readlines()
        for line in all_content:
            file_line.append(line.replace("\n",""))

    # 通过判断文件头来确定是否是M3U8文件
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True# 用来判断是否找到了下载的地址
    index = 16
    while index < len(file_line):
        # if index < 16: #去除多餘下載
        #     index = index + 1
        #     continue
        if "EXTINF" in file_line[index]:
            unknow = False
            tasks = []
            for i in [1, 3, 5, 7, 9]:#, 11, 13, 15, 17, 19
                if index+i < len(file_line):
                    tasks.append(get_ts(file_line[index+i],download_path))
            # 拼出ts片段的URL
            #pd_url = filePath.rsplit("/", 1)[0] + "/" + file_line[index + 1]
            await asyncio.gather(*tasks)
            index = index + i + 1
        else:
            break
    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print(u"下载完成")


async def get_ts(file_line,download_path):
    res = await requests.get(file_line)  # pd_url)
    c_file_name = str(file_line[file_line.find("vts") + 4:-4])
    async with aiofiles.open(download_path + "\\" + c_file_name + ".ts", 'ab') as f:
        await f.write(await res.read())
        await f.flush()
    #files = os.listdir(tsPath)
    #for file in range(2,files.count()):

def file_walker(path):
    file_list = []
    for root, dirs, files in os.walk(path):  # 生成器
        for fn in files:
            p = str(root + fn)
            file_list.append(p)

    #print(file_list)
    return file_list

async def combine(ts_path, combine_path, file_name):
        file_list = file_walker(ts_path)
        file_path = combine_path + file_name + '.mp4'
        async with aiofiles.open(file_path, 'wb+') as fw:
            for i in range(len(file_list)):
                await fw.write(open(file_list[i], 'rb').read())


async def run():
    m3u8Path = "D:\\m3u8\\m3u8\\"
    path = "D:\\m3u8\\"
    tsPath = "D:\\m3u8\\download\\"
    combinePath = "D:\\m3u8\\combine\\"
    jqsmM3u8Path = "D:\\m3u8\\m3u8\\jqsm\\"

    # combine(tsPath,combinePath,"浪货赵梦婷（第一集）")

    # with open(m3u8Path + "m3u8xiaoxianer.txt", "r", encoding="utf-8") as f:
    #     for line in f.readlines():
    #         spiltPos = line.find(":")
    #         fileName = line[:spiltPos]
    #         url = line[spiltPos + 1:]
    #         if os.path.exists(m3u8Path + fileName + ".m3u8") is True:
    #             continue
    #         else:
    #             await downloadM3u8(m3u8Path, fileName, url)

    for file in os.listdir(m3u8Path):
        # print(file.lower())

        fileName = file[:file.find(".")]
        fileType = file[file.find(".") + 1:]
        if os.path.exists(combinePath + fileName + ".mp4"):
            continue
        if fileType != "m3u8":
            continue
        await download(filePath=m3u8Path + file, download_path=tsPath)
        await combine(ts_path=tsPath, combine_path=combinePath, file_name=fileName)
        shutil.rmtree("D:\\m3u8\\download", True)
        os.mkdir("D:\\m3u8\\download")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

    #
