import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver import FirefoxOptions

location = "대구 북구 대학로 143"
url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
kakao_key = "8d7127274d16ab32508bc7b4936be2d4" # 보안주의~
result = requests.get(url, headers={"Authorization":f"KakaoAK {kakao_key}"})
json_obj = result.json()
x = json_obj['documents'][0]['x']
y = json_obj['documents'][0]['y']
# word = hostType
word = "정형외과"
final_url = f"https://m.place.naver.com/hospital/list?x={x}&y={y}&query={word}"
# opts = FirefoxOptions()
# opts.add_argument("--headless")
# browser = webdriver.Firefox(firefox_options=opts, executable_path = r'./geckodriver')
# browser.get(final_url)
browser = webdriver.Chrome("./chromedriver.exe")
browser.get(final_url)
# 목록보기 클릭
button = browser.find_element_by_class_name("_31ySW ")
button.click()
# 관련도순 클릭
time.sleep(1)
filter = browser.find_element_by_xpath('//*[@id="_list_scroll_container"]/div/div/div[1]/div/div/div/div/div/div/span[1]/a')
filter.click()
# 거리순으로 변경
time.sleep(1)
short_way = browser.find_element_by_xpath('//*[@id="_list_scroll_container"]/div/div/div[1]/div/div/div[2]/div/ul/li[2]/a')
short_way.click()