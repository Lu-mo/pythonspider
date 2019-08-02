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
import spider


def tryScrolling(driver):
    Action = TouchActions(driver)
    """从button元素像下滑动200元素，以50的速度向下滑动"""
    for i in range(2):
        time.sleep(5)
        # WebDriverWait(driver,10).until(EC.element_to_be_clickable((By.CSS_SELECTOR,)))
        Action.scroll_from_element(driver.find_element_by_css_selector("[class='mint-loadmore-bottom']"), 0,
                                   200).perform()

    sections, sectionsText = [], []
    sections, sectionsText = refreshSections(startPoint=listLen)
    return sections,sectionsText


def checkWebStatu(driver):
    #四号加载中
    #overflow: hidden; margin-top: 40px; 3
    print("\r 网页加载状态检测中...", end="")
    js = "if(document.querySelector(\"[class='mint-indicator']\")==null)" \
         "{return \"has no element\"}" \
         "else if(document.querySelector(\"[class='mint-indicator']\").hasAttribute(\"style\")==true){" \
         "return document.querySelector(\"[class='mint-indicator']\").style.display;" \
         "}" \
         "else" \
         "{" \
         "return \"has no style\";" \
         "}"
    result = driver.execute_script(js)
    while driver.execute_script(js) != "none":
        time.sleep(1)
        if driver.execute_script(js) == "has no element":
            time.sleep(3)
            #return False

    time.sleep(1)
    if driver.execute_script(js) == "none":
        print("\r 加载完成", end="")
        return True
    else:
        return checkWebStatu(driver)


def refreshSections(sections=[],sectionsText=[],startPoint=0):
    sections = []
    time.sleep(5)
    radioList = driver.find_element_by_css_selector("div#Target.unit.OrderList")
    temp = radioList.find_elements_by_css_selector("div#Target.unit.OrderList section.radioCardItemWrap")
    # driver.find_elements_by_css_selector("[id^=container]")[3].click()

    sectionsText = []
    for i in range(startPoint,len(temp)):
        sections.append(temp[i])
        tempText=temp[i].find_element_by_css_selector("div.title").text
        sectionsText.append(tempText)

    return sections,sectionsText

if __name__ == "__main__":
    txtSet = set()
    txtSet = spider.readTxtToSet('D:\\m3u8\\m3u8\\m3u8xiaoxianer.txt', txtSet=txtSet)

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

    caps = DesiredCapabilities.CHROME
    caps['loggingPrefs'] = {'performance': 'ALL'}

    driver = webdriver.Chrome(options=options, desired_capabilities=caps)
    driver.implicitly_wait(30)

    driver.get("http://kongjie58.space/mainview")

    spider.login(driver)



    # 定位分类，跳转分类_排行榜
    driver.find_elements_by_css_selector("[class^='unit navBtn']")[1].click()
    time.sleep(3)
    driver.find_elements_by_css_selector("[class='mint-tab-item-label']")[3].click()
    time.sleep(5)
    driver.find_elements_by_css_selector("[class='unit flex-left hostCardWrap']")[0].click()

    #定位每个节目
    #div#Target.unit.OrderList div:nth-child(1) section.radioCardItemWrap
    startPoint = 0
    sections, sectionsText = [], []
    sections, sectionsText = refreshSections(startPoint=startPoint)


    keepTrying = True

    while keepTrying == True:

        listLen = len(sections)

        startFlag = -1
        for sec in range(listLen):
            if sec <= startFlag:
                continue

            result = input(sectionsText[sec]+"\n"+
                            sections[sec].find_element_by_css_selector("ul").text+ " "+sections[sec].find_element_by_css_selector("div.count").text+"\n"
                               +"是否爬取该节目？((Y | 回车)/N)")
            if result.lower() == "n":
                continue

            # 进入二层目录
            try:
                sections[sec].click()
            except StaleElementReferenceException:
                sections, sectionsText = refreshSections(startPoint=startPoint)
                sections[sec].click()
            time.sleep(5)

            checkWebStatu(driver)
            # 获取二层节目列表
            # listcount 节目数
            radioList = driver.find_element_by_css_selector("[class='radioList']")
            radioList = radioList.find_elements_by_css_selector("[class='flex-left flex-middle radioCard']")
            listCount = 0
            listCount = len(radioList)

            #div.flex-left.flex-middle.radioCard:nth-child(3)
            radioNameList = driver.find_elements_by_css_selector("div.radioList>div.flex-left.flex-middle.radioCard>div.unit.radioTItle>div.title")
            radioNameTextList = list()
            for eachRadioName in radioNameList:
                radioNameTextList.append(eachRadioName.text)

            # 如果节目单只有一个节目且已经爬去，直接返回上一层
            radioName = radioList[0].text
            radioName = radioName[:radioName.find("\n")]
            if listCount == 1 and radioName in txtSet:
                checkWebStatu(driver)
                driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
                continue

            urlToNameDict = dict()
            logIndex = 0
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
                    # while driver.find_element_by_css_selector("[class='mint-indicator']").is_displayed():
                    #     time.sleep(1)
                    checkWebStatu(driver)
                    esp.click()

                checkWebStatu(driver)
                #time.sleep(5)
                # storage=LocalStorage(driver)
                radioName = driver.find_element_by_css_selector("[class='mint-header-title']").text
                if radioName in txtSet:
                    checkWebStatu(driver)
                    time.sleep(3)
                    backButton = driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
                    continue

                checkWebStatu(driver)
                urlToNameDict[driver.current_url] = radioName
                # 相当于获取F12Network选项卡的内容,结构应该是栈,后进内容先提取
                # 提取带有m3u8的链接,写入文件存储
                # 这一段不太严谨，无法保证链接与节目一一对应,但目前没有出过错
                logs = [json.loads(log['message'])['message'] for log in driver.get_log('performance')]
                logsProcessed = []
                for each in logs:
                    if each["method"] == 'Network.requestWillBeSent':
                        try:
                            referer = each["params"]["request"]["headers"]["Referer"]
                            each = each["params"]["request"]["url"]
                            begin = each.find("m3u8?")
                            if begin != -1:
                                logsProcessed.append(urlToNameDict.get(referer) + ":" + each)
                                #break
                        except:
                            continue
                t = json.dumps(logsProcessed)
                with open('D:\\m3u8\\m3u8\\m3u8xiaoxianer.txt', 'a', encoding="utf-8") as f:
                    for line in logsProcessed:
                        f.write("%s\n" % line)

                checkWebStatu(driver)
                backButton = driver.find_element_by_css_selector("[class='mintui mintui-back']").click()
                # 本页节目单爬取完毕,返回
            checkWebStatu(driver)
            driver.find_element_by_css_selector("[class='mintui mintui-back']").click()

        sections, sectionsText = tryScrolling(driver)

        while keepTrying ==True:
            if len(sections) == 0:
                result = input("应该已经到达页面底端,是否继续尝试(Y/N)")
                result = result.lower()
            else:
                break
            if result == "n":
                keepTrying = False
            else:
                keepTrying = True
                sections, sectionsText = tryScrolling(driver)
        startPoint = len(sections)

    print("done")