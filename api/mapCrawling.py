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