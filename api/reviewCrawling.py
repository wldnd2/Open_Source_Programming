# -*- coding: utf-8 -*-

# %matplotlib inline

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings
warnings.filterwarnings("ignore")

import time
import requests
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options
from selenium.webdriver import FirefoxOptions

import re

def text_cleaning(text):
    try:
        hangul = re.compile('[^ ㄱ-ㅣ가-힣+]') # 한글과 띄어쓰기를 제외한 모든 글자
        result = hangul.sub('', text) # 한글과 띄어쓰기를 제외한 모든 부분을 제거
        return (result)
    except:
        return text

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


columns = ['score', 'review']
df = pd.DataFrame(columns=columns)

opts = FirefoxOptions()
opts.add_argument("--headless")
driver = webdriver.Firefox(firefox_options=opts, executable_path = r'./geckodriver')
page_url = page_urls[0]
    
driver.get(page_url)
time.sleep(2)

html = driver.page_source
soup = BeautifulSoup(html, 'html.parser')
contents_div = soup.find(name="div", attrs={"class":"evaluation_review"})
rates = contents_div.find_all(name="em", attrs={"class":"num_rate"})
reviews = contents_div.find_all(name="p", attrs={"class":"txt_comment"})
  
for rate, review in zip(rates, reviews):
    row = [rate.text[0], review.find(name="span").text]
    series = pd.Series(row, index=df.columns)
    df = df.append(series, ignore_index=True)
    # 2-5페이지의 리뷰를 크롤링합니다
for button_num in range(2, 6):
    # 오류가 나는 경우(리뷰 페이지가 없는 경우), 수행하지 않습니다.
    try:
        another_reviews = driver.find_element_by_xpath("//a[@data-page='" + str(button_num) + "']")
        another_reviews.click()
        time.sleep(2)
        # 페이지 리뷰를 크롤링합니다
        html = driver.page_source
        soup = BeautifulSoup(html, 'html.parser')
        contents_div = soup.find(name="div", attrs={"class":"evaluation_review"})
        # 별점을 가져옵니다.
        rates = contents_div.find_all(name="em", attrs={"class":"num_rate"})
        # 리뷰를 가져옵니다.
        reviews = contents_div.find_all(name="p", attrs={"class":"txt_comment"})
        for rate, review in zip(rates, reviews):
            row = [rate.text[0], review.find(name="span").text]
            series = pd.Series(row, index=df.columns)
            df = df.append(series, ignore_index=True)
    except:
        break
driver.close()

df['y'] = df['score'].apply(lambda x: 1 if float(x) > 3 else 0)
# print(df.shape)
df.head()
df.to_csv("review_data.csv", index=False)
df = pd.read_csv("review_data.csv")

df = pd.read_csv("review_data.csv")
df['ko_text'] = df['review'].apply(lambda x: text_cleaning(x))
del df['review']

df = df[df['ko_text'].str.len() > 0]
df.head()

from konlpy.tag import Okt
def get_pos(x):
    tagger = Okt()
    pos = tagger.pos(x)
    pos = ['{}/{}'.format(word,tag) for word, tag in pos]
    return pos

result = get_pos(df['ko_text'].values[0])
# print(result)

from sklearn.feature_extraction.text import CountVectorizer

index_vectorizer = CountVectorizer(tokenizer = lambda x: get_pos(x))
X = index_vectorizer.fit_transform(df['ko_text'].tolist())
X.shape
# print(str(index_vectorizer.vocabulary_)[:100]+"..")
# print(df['ko_text'].values[0])
# print(X[0])

from sklearn.feature_extraction.text import TfidfTransformer
# TF-IDF 방법으로, 형태소를 벡터 형태의 학습 데이터셋(X 데이터)으로 변환
tfidf_vectorizer = TfidfTransformer()
X = tfidf_vectorizer.fit_transform(X)
# print(X.shape)
# print(X[0])
