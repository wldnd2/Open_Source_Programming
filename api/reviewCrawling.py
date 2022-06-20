import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxOptions

# 병원 url찾기
opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts, executable_path = r'./geckodriver')

# browser.get(final_url)
# driver = webdriver.Chrome("./chromedriver.exe")

source_url = "https://map.kakao.com/"
driver.get(source_url)

searchbox = driver.find_element_by_xpath("//input[@id='search.keyword.query']")
searchbox.send_keys("최병원")

searchbutton = driver.find_element_by_xpath("//button[@id='search.keyword.submit']")
driver.execute_script("arguments[0].click();", searchbutton)

time.sleep(2)
html = driver.page_source

# 병원 url 크롤링
soup = BeautifulSoup(html, "html.parser")
moreviews = soup.find_all(name="a", attrs={"class":"moreview"})

page_urls = []
for moreview in moreviews:
    page_url = moreview.get("href")
    print(page_url)
    page_urls.append(page_url)

driver.close()