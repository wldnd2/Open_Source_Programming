#!/usr/bin/python
#-*- coding: utf-8 -*-

from re import template
from api import mapCrawling
from symptoms_module import *
import random
from bs4 import BeautifulSoup
from flask import Flask, render_template, request

app = Flask(__name__)
app.register_blueprint(map.bp,url_prefix='/map') #map.py에 있는 bp를 /map 뒤에 등록한다.
#app.register_blueprint(calc.bp)#꼬리표 없으니까 실행했을때 첨으로 켜짐
#너무 복잡해질까봐 빼놓은거

@app.route('/', methods=['GET'])
def input():
    return render_template('index.html')

@app.route('/project_2',methods=['POST'])
def result():
    part = request.form['part']
    sym = request.form['sym']
    if part=="배":
    	Diction = stomach_symptoms(sym)
    elif part=="머리":
    	Diction = head_symptoms(sym)
    elif part=="목":
    	Diction = neck_symptoms(sym)
    elif part=="가슴":
    	Diction = chest_symptoms(sym)
    elif part=="등":
    	Diction = back_symptoms(sym)
    elif part=="엉덩이":
    	Diction = hip_symptoms(sym)
    elif part=="팔":
    	Diction = arm_symptoms(sym)
    elif part=="다리":
    	Diction = leg_symptoms(sym)

    
    kakao_key = "97c23c3cc66e3885bde6a88ecdcbd7be"
    return render_template('project_2.html', kakao_key = kakao_key, contents=Diction)

if __name__ == '__main__':
    app.run(host = "127.0.0.1:5000")
