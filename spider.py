import json
import time
import pycurl
import os
from io import BytesIO
from selenium import webdriver
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.touch_actions import TouchActions

from LocalStorage import LocalStorage


def login(driver):
    driver.find_elements_by_css_selector("[class='m-tabbar-item-text']")[4].click()
    # 登录模块
    driver = writeCookieAndLocalStorage(driver)
    driver.refresh()
    WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.m-tabbar.flex-left>a.m-tabbar-item.unit:nth-child(5)")))
    time.sleep(3)
    # 检测右下角(第五个选项卡)标签显示，检测localStorage登录是否成功,成功切换为选项卡1
    if driver.find_elements_by_css_selector("[class='m-tabbar-item-text']")[4].text.replace(" ", "") != "我的":
        driver = loginManually(driver)
    driver.find_elements_by_css_selector("[class='m-tabbar-item-text']")[0].click()


def checkWebStatu(driver):
    print("\r 网页加载状态检测中...",end="")
    js="if(document.querySelector(\"[class='mint-indicator']\")==null)" \
       "{return \"has no element\"}" \
       "else if(document.querySelector(\"[class='mint-indicator']\").hasAttribute(\"style\")==true){" \
       "return document.querySelector(\"[class='mint-indicator']\").style.display;" \
       "}" \
       "else" \
       "{" \
       "return \"has no style\";" \
       "}"
    result=driver.execute_script(js)
    while driver.execute_script(js) != "none":
        time.sleep(1)
        if driver.execute_script(js) == "has no element":
            time.sleep(3)
            return False
    time.sleep(1)
    if driver.execute_script(js) == "none":
        print("\r 加载完成", end="")
        return True
    else:
        return checkWebStatu(driver)


def refreshSections(sections,sectionsText,pageNum):
    time.sleep(5)
    page = driver.find_elements_by_css_selector("[class^='swiper-slide swiper-slide-active']")
    sections=[]
    sections = page[pageNum].find_elements_by_css_selector("[id^=container]")
    # driver.find_elements_by_css_selector("[id^=container]")[3].click()

    sectionsText = []
    for i in range(len(sections)):
        sectionsText.append(sections[i].text)

    return sections,sectionsText


def loginManually(driver):
    '''
        检测登录状态,看是否需要手动登陆
    '''
    result=""
    statu = driver.find_elements_by_css_selector("[class='m-tabbar-item-text']")[4].text.replace(" ", "")
    if statu == "我的":
        print("已登陆")
        result="y"
    else:
        result = input("---------------------请手动登陆,登陆完成后回车:---------------------------")
        #driver.get("http://kongjie58.space/mainview")
        time.sleep(3)
        statu = driver.find_elements_by_css_selector("[class='m-tabbar-item-text']")[4].text.replace(" ","")
        if statu == "我的":
            result="y"
        else:
            result="n"
    # 获取cookie并通过json模块将dict转化成str
    dictCookies = driver.get_cookies()
    jsonCookies = json.dumps(dictCookies)
    # 登录完成后，将cookie保存到本地文件
    with open('C:\\Users\\yxt91\\data\\cookies.json', 'w') as f:
        f.write(jsonCookies)

    storage=LocalStorage(driver)
    #print(storage.items())
    jsonStorage = json.dumps(storage.items())
    with open('C:\\Users\\yxt91\\data\\Storage.json', 'w') as f:
        f.write(jsonStorage)

    if result is "y":
        driver=writeCookieAndLocalStorage(driver)
    else:
        print("未成功登录,程序退出")
        os._exit(0)


    return driver


def writeCookieAndLocalStorage(driver):
    # 初次建立连接，随后方可修改cookie
    #driver.get("http://kongjie58.space/mainview")
    # 删除第一次建立连接时的cookie
    #driver.delete_all_cookies()
    # 读取登录时存储到本地的cookie
    with open('C:\\Users\\yxt91\\data\\cookies.json', 'r', encoding='utf-8') as f:
        listCookies = json.loads(f.read())
    for cookie in listCookies:
        driver.add_cookie({
            'domain': cookie['domain'],  # 此处xxx.com前，需要带点
            'expiry': cookie['expiry'] if (('expiry' in cookie) is True) else 0,
            'httpOnly': cookie['httpOnly'],
            'name': cookie['name'],
            'path': '/',
            'secure': cookie['secure'],
            'value': cookie['value']
        })

    storage = LocalStorage(driver)
    # storage.set("tempname","xbspider")
    # storage.set("temppass","xbspider123")
    storage.clear()
    # if storage.get("__insp_lml") == None:
    #     return driver
    with open('C:\\Users\\yxt91\\data\\Storage.json', 'r', encoding='utf-8') as f:
        listStorage = json.loads(f.read())
    for Storage in listStorage:
        # if Storage != "__insp_lml":
        storage.set(Storage, listStorage[Storage])
        # print(Storage+":"+listStorage[Storage])

    return driver


def checkRadioName(radioName,filePath):
    with open(filePath, 'r', encoding="utf-8") as f:
        f.readlines()


def readTxtToSet(filePath,txtSet):
    with open(filePath,"r",encoding="utf-8") as f:
        for line in f.readlines():
            end=line.find(":")
            txtSet.add(line[:end])
    return txtSet


def getIPProxy():
    buffer = BytesIO()
    s =""
    curl = pycurl.Curl()
    curl.setopt(curl.URL, 'http://ip.jiangxianli.com/api/proxy_ip')
    curl.setopt(curl.WRITEDATA, buffer)
    curl.perform()
    curl.close()
    body = buffer.getvalue()
    s = body.decode('unicode_escape')
    #print(s.decode())
    IPJson = json.loads(s)
    #print(body.decode('utf-8'))
    #print(s)
    return IPJson["data"]

if __name__=="__main__":
    '''
    program begin
    '''
    txtSet = set()
    txtSet = readTxtToSet('D:\\m3u8\\m3u8\\m3u8.txt', txtSet=txtSet)

    options = webdriver.ChromeOptions()
    # 禁止加载图片和JS
    prefs = {
        'profile.default_content_setting_values': {
            'images': 2,
            # 'javascript':2
        }
    }

    options.add_experimental_option("prefs", prefs)
    options.add_experimental_option('w3c', False)
    options.add_argument("--mute-audio")
    # 设置代理，放弃,代理质量太差
    # data = getIPProxy()
    # options.add_argument("--proxy-server="+data["protocol"]+"://"+data["ip"]+":"+data["port"])

    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    driver.implicitly_wait(20)

    driver.get("http://kongjie58.space/mainview")

    login(driver)

    sections, sectionsText = [], []
    sections, sectionsText = refreshSections(sections, sectionsText, 0)

    # 定位分类，跳转分类
    driver.find_elements_by_css_selector("[class^='unit navBtn']")[4].click()

    # 选择细致分类
    WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,
                                                                "div.swiper-slide.swiper-slide-active button.popVideo-right-menu.popVideo-right-menu.unit-0.flex-right.flex-middle")))
    driver.find_element_by_css_selector(
        "div.swiper-slide.swiper-slide-active button.popVideo-right-menu.popVideo-right-menu.unit-0.flex-right.flex-middle").click()
    time.sleep(2)
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, "div.swiper-slide.swiper-slide-active li:nth-child(2)>a")))
    driver.find_elements_by_css_selector("div.swiper-slide.swiper-slide-active li>a")[1].click()

    # 定位“上拉加载更多”
    bottoms = driver.find_elements_by_css_selector("[class=mint-loadmore-bottom]")

    # 去除广告阻挡
    # 方案一 点击关闭,在设置不加载图片后 失效
    # driver.find_element_by_css_selector("[class='unit-0 X flex-middle']").click()
    # 方案二 隐藏元素
    js = "document.querySelector(\"[class='popInfo']\").style.display='none';"
    driver.execute_script(js)

    # 疯狂上拉
    Action = TouchActions(driver)
    """从button元素像下滑动200元素，以50的速度向下滑动"""
    for i in range(6):
        time.sleep(5)
        # WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,)))
        Action.scroll_from_element(bottoms[3], 0, 200).perform()

    # time.sleep(5)
    sections, sectionsText = refreshSections(sections, sectionsText, 1)

    listLen = len(sections)

    tempFlag = 21
    for sec in range(listLen):
        if sec <= tempFlag:
            continue

        # 点击进入二层节目列表
        try:
            sections[sec].click()
        except StaleElementReferenceException:
            sections, sectionsText = refreshSections(sections, sectionsText, 1)
            sections[sec].click()
        time.sleep(5)

        checkWebStatu(driver)
        # 获取二层节目列表
        # listcount 节目数
        radioList = driver.find_element_by_css_selector("[class='radioList']")
        radioList = radioList.find_elements_by_css_selector("[class='flex-left flex-middle radioCard']")
        listCount = 0
        listCount = len(radioList)

        # 如果节目单只有一个节目且已经爬去，直接返回上一层
        # startFlag = -1
        radioName = radioList[0].text
        radioName = radioName[:radioName.find("\n")]
        if listCount == 1 and radioName in txtSet:
            checkWebStatu(driver)
            driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
            continue

        for i in range(listCount):

            # 进出节目页面后,定位的节目元素会失效，需重新定位
            radioList = driver.find_element_by_css_selector("[class='radioList']").find_elements_by_css_selector(
                "[class='flex-left flex-middle radioCard']")
            esp = radioList[i]

            # 已经爬取,跳过
            radioName = esp.text
            radioName = radioName[:radioName.find("\n")]
            if radioName in txtSet:
                continue

            # 进入节目页面
            try:
                while driver.find_element_by_css_selector("[class='mint-indicator']").is_displayed():
                    time.sleep(3)
                time.sleep(1)
            finally:
                tCSS = "div.radioList>div.flex-left.flex-middle.radioCard:nth-child(" + str(i + 1) + ")"
                WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, tCSS)))
                while driver.find_element_by_css_selector("[class='mint-indicator']").is_displayed():
                    time.sleep(1)
                esp.click()

            time.sleep(5)
            # storage=LocalStorage(driver)
            radioName = driver.find_element_by_css_selector("[class='mint-header-title']").text
            if radioName in txtSet:
                checkWebStatu(driver)
                backButton = driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
                continue

            # 相当于获取F12Network选项卡的内容,结构应该是栈,后进内容先提取
            # 提取带有m3u8的链接,写入文件存储
            # 这一段不太严谨，无法保证链接与节目一一对应,但目前没有出过错
            logs = [json.loads(log['message'])['message'] for log in driver.get_log('performance')]
            logsProcessed = []
            for each in logs:
                if each["method"] == 'Network.requestWillBeSent':
                    try:
                        each = each["params"]["request"]["url"]
                        begin = each.find("m3u8?")
                        if begin != -1:
                            logsProcessed.append(radioName + ":" + each)
                    except:
                        continue
            t = json.dumps(logsProcessed)
            with open('C:\\Users\\yxt91\\data\\m3u8.txt', 'a', encoding="utf-8") as f:
                for line in logsProcessed:
                    f.write("%s\n" % line)

            # 放弃从localStorage 获取 该键值对会诡异消失,可能是登陆的问题
            # insp_lml = ""
            # insp_lml = driver.execute_script("return window.localStorage.getItem(arguments[0]);", '__insp_lml')
            # begin = insp_lml.find("https://radioluntan.space/apiv286.m3u8?request=3DTX")
            # end = insp_lml.find("\"", begin)
            # # m3u8  link
            # print(radioName + ":" + insp_lml[begin:end])
            # 该节目爬取完毕,继续下一个节目
            checkWebStatu(driver)
            backButton = driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
        # 本页节目单爬取完毕,返回
        checkWebStatu(driver)
        driver.find_element_by_css_selector("[class='mintui mintui-back']").click()

    # driver.execute_script("localstorage.getItem('__insp_lml')")