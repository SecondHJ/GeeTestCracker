# coding: utf-8
import time
from selenium import webdriver
from selenium.webdriver.common.action_chains import ActionChains
import urllib2
import ImageUtil
from PIL import Image
import re
import random
from selenium.webdriver.remote.command import Command

# 打开目标网站
browser = webdriver.Chrome()
browser.get("http://www.gsxt.gov.cn/index.html")
time.sleep(5)
# 输入搜索内容并查询
browser.find_element_by_css_selector("#keyword").send_keys("sbsbsbssb")
time.sleep(3)
browser.find_element_by_css_selector("#btn_query").click()
time.sleep(6)
# 图片下载还原并计算距离
html = browser.page_source
bgUrl = re.findall("http://static\.geetest\.com/pictures/gt/[0-9|a-z]{9}/bg/[0-9|a-z]{9}", html)
fullbgUrl = re.findall("http://static\.geetest\.com/pictures/gt/[0-9|a-z]{9}/[0-9|a-z]{9}", html)
bgUrl = str(bgUrl[0]) + ".jpg"
fullbgUrl = str(fullbgUrl[0]) + ".jpg"
print bgUrl
print fullbgUrl
# 下载图片
getPicHeader = {
    'Host': 'static.geetest.com',
    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'Referer': 'http://www.gsxt.gov.cn/corp-query-search-1.html',
    'origin': 'http://www.gsxt.gov.cn',
    'Connection': 'keep-alive',

}

print "正在下载图片..."
request = urllib2.Request(bgUrl, headers=getPicHeader)
bgResult = urllib2.urlopen(request)
with open("seleniumCaptcha/bg.png", "wb") as f:
    f.write(bgResult.read())

request = urllib2.Request(fullbgUrl, headers=getPicHeader)
fullbgResult = urllib2.urlopen(request)
with open("seleniumCaptcha/fullbg.png", "wb") as f:
    f.write(fullbgResult.read())
print "图片下载完成"

print "正在还原图片...."
# 图像还原
#  X偏移值: (n[i] % 26 * 12 + 1)
#  Y偏移值: (n[i] > 25 ? f.config.height / 2 : 0)
# 恢复前图像
bg = Image.open("seleniumCaptcha/bg.png", "r")
fullbg = Image.open("seleniumCaptcha/fullbg.png", "r")
rows = 2  # 行
columns = 26  # 列
sliceWidth = 10  # 列宽
sliceHeight = 58  # 行高
#  创建恢复后图像
recoverBg = Image.new("RGBA", (columns * sliceWidth, rows * sliceHeight))
recoverFullBg = Image.new("RGBA", (columns * sliceWidth, rows * sliceHeight))

n = [39, 38, 48, 49, 41, 40, 46, 47, 35, 34, 50, 51, 33, 32, 28, 29, 27, 26, 36, 37, 31, 30, 44, 45, 43, 42, 12, 13,
     23,
     22, 14, 15, 21, 20, 8, 9, 25, 24, 6, 7, 3, 2, 0, 1, 11, 10, 4, 5, 19, 18, 16, 17]
startingX = 0
startingY = 0
offsetX = 0
offsetY = 0
for row in range(rows):
    for column in range(columns):
        startingX = column * sliceWidth
        startingY = row * sliceHeight
        offsetX = n[row * columns + column] % 26 * 12 + 1
        if n[row * columns + column] > 25:
            offsetY = int(116 / 2)
        else:
            offsetY = 0
        for x in range(sliceWidth):
            for y in range(sliceHeight):
                bgPix = bg.getpixel((offsetX + x, offsetY + y))
                recoverBg.putpixel((startingX + x, startingY + y),
                                   bgPix)
                fullbgPix = fullbg.getpixel((offsetX + x, offsetY + y))
                recoverFullBg.putpixel((startingX + x, startingY + y),
                                       fullbgPix)

# 保存恢复后图像
recoverBg.save("seleniumCaptcha/recoverBg.png", "PNG")
recoverFullBg.save("seleniumCaptcha/recoverFullBg.png", "PNG")
print "还原图片完成"
print "正在计算缺块距离..."
# 计算缺块的距离
breakFlag = 0
length = 0
for x in range(recoverBg.size[0]):
    for y in range(recoverBg.size[1]):
        isSimilar = ImageUtil.pixSimilar(recoverBg.getpixel((x, y)), recoverFullBg.getpixel((x, y)))
        if isSimilar is False:
            length = x - 5
            breakFlag = 1
            break
    if breakFlag == 1:
        break
print "缺块距离" + str(length)

# # 执行拖拽
print "正在执行拖拽....."
block = browser.find_element_by_css_selector(".gt_slider_knob")
acthion = ActionChains(browser)
acthion.click_and_hold(block).perform()
time.sleep(random.randint(1, 32) * 0.01)
# 拖拽
for index in range(length):
    browser.execute(Command.MOVE_TO, {'xoffset': 1, 'yoffset': random.randint(-1, 1)})
    time.sleep(random.randint(39, 698) * 0.0001)
    if index == length - 15:
        for index in range(3):
            browser.execute(Command.MOVE_TO, {'xoffset': 9999, 'yoffset': 9999})
            browser.execute(Command.MOVE_TO, {'xoffset': -9999, 'yoffset': -9999})
time.sleep(random.randint(0, 100) * 0.001)
acthion.release(block).perform()
time.sleep(2)
browser.close()
