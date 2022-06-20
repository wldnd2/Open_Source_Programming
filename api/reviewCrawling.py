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


# 긍정, 부정 리뷰 분류하기
from sklearn.model_selection import train_test_split

y = df['y']
x_train, x_test, y_train, y_test = train_test_split(X, y, test_size=0.30)
# print(x_train.shape)
# print(x_test.shape)

from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score

# 로지스틱 회귀모델 학습
lr = LogisticRegression(random_state=0)
lr.fit(x_train, y_train)
y_pred = lr.predict(x_test)
y_pred_probability = lr.predict_proba(x_test)[:,1]

# 로지스틱 회귀모델의 성능 평가
# print("accuracy: %.2f" % accuracy_score(y_test, y_pred))
# print("Precision : %.3f" % precision_score(y_test, y_pred))
# print("Recall : %.3f" % recall_score(y_test, y_pred))
# print("F1 : %.3f" % f1_score(y_test, y_pred))

from sklearn.metrics import confusion_matrix

confmat = confusion_matrix(y_true=y_test, y_pred=y_pred)
# print(confmat)


# 그래프 출력
from sklearn.metrics import roc_curve, roc_auc_score

# AUC계산
false_positive_rate, true_positive_rate, thresholds = roc_curve(y_test, y_pred_probability)
roc_auc = roc_auc_score(y_test, y_pred_probability)
# print("AUC : %.3f" % roc_auc)

# ROC curve 그래프 출력
plt.rcParams['figure.figsize'] = [5, 4]
plt.plot(false_positive_rate, true_positive_rate, label='ROC curve (area = %0.3f)' % roc_auc, 
         color='red', linewidth=4.0)
plt.plot([0, 1], [0, 1], 'k--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.0])
plt.xlabel('False Positive Rate')
plt.ylabel('True Positive Rate')
plt.title('ROC curve of Logistic regression')
plt.legend(loc="lower right")

# 학습한 회귀 모델 계수출력.
plt.rcParams['figure.figsize'] = [10, 8]
plt.bar(range(len(lr.coef_[0])), lr.coef_[0])

print(sorted(((value, index) for index, value in enumerate(lr.coef_[0])), reverse=True)[:5])
print(sorted(((value, index) for index, value in enumerate(lr.coef_[0])), reverse=True)[-5:])

# 회귀 모델의 계수를 높은 순 정렬 
coef_pos_index = sorted(((value, index) for index, value in enumerate(lr.coef_[0])), reverse=True)

# 회귀 모델의 계수를 index_vectorizer에 맵핑 -> 어떤 형태소인지 출력
invert_index_vectorizer = {v: k for k, v in index_vectorizer.vocabulary_.items()}

# 계수가 높은 순으로, 피처에 형태소를 맵핑한 결과를 출력
# 계수가 높은 피처는 리뷰에 긍정적인 영향을 주는 형태소
print(str(invert_index_vectorizer)[:100]+'..')

# 상위 20개 긍정 형태소 출력
for coef in coef_pos_index[:20]:
    print(invert_index_vectorizer[coef[1]], coef[0])
# 상위 20개 부정 형태소 출력
for coef in coef_pos_index[-20:]:
    print(invert_index_vectorizer[coef[1]], coef[0])

# 최종 결과 분석

# 긍정!!!
positive_noun_list = []
positive_adjective_list = []

# 명사, 형용사별로 계수가 높은 상위 10개의 형태소 추출
for coef in coef_pos_index[:100]:
    pos_category = invert_index_vectorizer[coef[1]].split("/")[1]
    if pos_category == "Noun":
        positive_noun_list.append((invert_index_vectorizer[coef[1]], coef[0]))
    elif pos_category == "Adjective":
        positive_adjective_list.append((invert_index_vectorizer[coef[1]], coef[0]))

print("긍정적인 명사 리뷰:")
for i in range(0,5):
    print(positive_noun_list[i][0][:-5])
print("긍정적인 형용사 리뷰:")
for i in range(0,5):
    print(positive_adjective_list[i][0][:-10])

# 부정!!!
negative_noun_list = []
negative_sadjective_list = []

# 명사, 형용사별로 계수가 높은 상위 10개의 형태소 추출
for coef in coef_pos_index[-50:]:
    pos_category = invert_index_vectorizer[coef[1]].split("/")[1]
    if pos_category == "Noun":
        negative_noun_list.append((invert_index_vectorizer[coef[1]], coef[0]))
    elif pos_category == "Adjective":
        negative_sadjective_list.append((invert_index_vectorizer[coef[1]], coef[0]))

print("부정적인 명사 리뷰:")
for i in range(0,5):
    print(negative_noun_list[i][0][:-5])
print("부정적인 형용사 리뷰:")
for i in range(0,5):
    print(negative_sadjective_list[i][0][:-10])