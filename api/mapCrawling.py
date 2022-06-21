import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

def extract_hospital(html, browser, index):
    #-------------------------------
    try:
        path = '//*[@id="_list_scroll_container"]/div/div/div[2]/ul/li[{0}]/div[2]/div/div/span[2]/a/span[2]/*[local-name()="svg"]'.format(index)
        moreInfo = browser.find_element_by_xpath(path)
        moreInfo.click()
        time.sleep(0.5)
        # 아무래도 주소값은 셀레니움으로 긁어와야 할듯 하다
        temp = BeautifulSoup(browser.page_source, 'html.parser')
        address = temp.find("span", class_="_1sG9K").next_sibling.get_text()
        moreInfo.click()
    except:
        address = "No information!"
    #-------------------------------
    try:
        location = address
        url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
        kakao_key = "8d7127274d16ab32508bc7b4936be2d4" # 보안주의~
        result = requests.get(url, headers={"Authorization":f"KakaoAK {kakao_key}"})
        json_obj = result.json()
        x = json_obj['documents'][0]['x']
        y = json_obj['documents'][0]['y']
        # print(x,y)
        x, y = str(x), str(y)
        temp = [x,y]
    except:
        return
    #-------------------------------
    # 거리
    distance = html.select("div._3fqfH > span")[0].text
    # 병원 이름
    title = html.select("div.nfZUc > span")[0].text
    # 영업시간
    try:
        when = html.find("span", class_="_2P75l").next_sibling.get_text()
        if "블로그" in when:
            when = "정보가 없어요"
    except:
        # when = "ERROR!!!!"
        when = "정보가 없어요"
    finally:
        result = [distance, title, when, address, temp]
        return result

def Crawler(hostType):
    location = "대구 북구 대학로 143"
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
    kakao_key = "8d7127274d16ab32508bc7b4936be2d4" # 보안주의~
    result = requests.get(url, headers={"Authorization":f"KakaoAK {kakao_key}"})
    json_obj = result.json()
    # print(json_obj)
    x = json_obj['documents'][0]['x']
    y = json_obj['documents'][0]['y']
    # print(y, x)
    word = hostType
    final_url = f"https://m.place.naver.com/hospital/list?x={x}&y={y}&query={word}"
    # opts = FirefoxOptions()
    # opts.add_argument("--headless")
    # browser = webdriver.Firefox(firefox_options=opts, executable_path = r'./geckodriver')
    # browser.get(final_url)
    options = webdriver.ChromeOptions()
    options.add_argument("headless")
    # browser = webdriver.Chrome("./chromedriver.exe", chrome_options=options)
    browser = webdriver.Chrome(service=Service(ChromeDriverManager().install()), chrome_options=options)
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
    # 크롤링 시작!!
    time.sleep(1)
    inf = []
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    hospitals = soup.find_all("li", class_="_2JXhh")
    # print(hospitals)
    # print(len(hospitals)) # 50개니까 완전 충분함  
    index = 1
    for hospital in hospitals:
        information = extract_hospital(hospital, browser, index)
        if information is not None:
            inf.append(information)
        if index > 2:
            break
        index += 1
    browser.quit()
    return inf
