#83
#137
import requests
import os
import time
#print("downloading with requests")
def downloadM3u8(path,fileName,url):
    #url = 'https://radioluntan.space/apiv286.m3u8?request=3DTXnd8fqSVbdQSsymV8NTV5y16yduUkMOnguZBOCoH6YuKRk4tFLsJp%2BIheovJ8mDgYyvZq0j2U9GlP7hXaYYZ9dxtknVg0glSFsx4m58V%2FBsdYDvIrrKwGdQBZB9qHKG5y6feBrDrS27eUtWqpJXd%2BbFoMo0mfBfJen2ljBEJh5zT8bl3hvXxhxMvOilo3b1YB1f%2B0GpZUwhHKdpD1U4apoKnHGvtNB6RTOVDgBvhyRPPKBBSoS%2FD8lqUPndDDsgdG7uaqQC7EyLH5jDBMk79oU8ua7CYGsVf0NqIc1Hx0hAMTInQWyFuOFDHgHgWq%2Fm5C5TnxfXp8I1RMx4YQmxddmzT4LJTmWv5458DsIVE%3D'
    r = requests.get(url)
    with open(path + fileName + ".m3u8", "wb") as code:
        code.write(r.content)


def download(filePath):
    download_path = "D:\\m3u8\\download"#os.getcwd() + "\download"
    if not os.path.exists(download_path):
        os.mkdir(download_path)
    #all_content = requests.get(filePath).text# 获取M3U8的文件内容
    #file_line = all_content.split("\r\n")  # 读取文件里的每一行
    file_line = list()
    with open(filePath, "r", encoding="utf-8") as f:
        all_content = f.readlines()
        for line in all_content:
            file_line.append(line.replace("\n",""))

    # 通过判断文件头来确定是否是M3U8文件
    if file_line[0] != "#EXTM3U":
        raise BaseException(u"非M3U8的链接")
    else:
        unknow = True# 用来判断是否找到了下载的地址
    for index, line in enumerate(file_line):
        if "EXTINF" in line:
            unknow = False
            # 拼出ts片段的URL
            #pd_url = filePath.rsplit("/", 1)[0] + "/" + file_line[index + 1]
            res = requests.get(file_line[index + 1])#pd_url)
            c_fule_name = str(file_line[index + 1][file_line[index + 1].find("vts")+4:-4])
            with open(download_path + "\\" + c_fule_name+".ts", 'ab') as f:
                f.write(res.content)
                f.flush()
    if unknow:
        raise BaseException("未找到对应的下载链接")
    else:
        print(u"下载完成")




path = "D:\\m3u8\\m3u8\\"

#download(path+"浪货赵梦婷（第一集）.m3u8")
list = list()
with open(path+"m3u8.txt","r",encoding="utf-8") as f:
    for line in f.readlines():
        spiltPos = line.find(":")
        fileName = line[:spiltPos]
        url = line[spiltPos+1:]
        if os.path.exists(path+fileName+".m3u8")==True:
            continue
        else:
            downloadM3u8(path,fileName,url)