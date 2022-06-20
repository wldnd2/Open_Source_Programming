from re import template
from api import map #api 폴더에 있는 map.py 파일 가져온거
from api import mapCrawling, kakaoMap
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

	# Diction = {'알코올성 간질환(Alcoholic liver disease)': ['소화기내과'],'간질환(Alcoholic liver disease)': ['소화기내과']}
	r = []
	index = 0
	sym = []
	# 삭제한 키값 리스트
	removeKey = []
	# 랜덤 인덱스 값
	rndIndex = []
	# 결과로 나온 증상들의 지도 결과 값을 받는다.
	for key, value in Diction.items():
		try:
			rnd = random.randrange(1,4)
			try:
				temp = [key, list(Diction.values())[index][rnd]]
			except:
				rnd = 0
				temp = [key, list(Diction.values())[index][rnd]]
			crawResult = mapCrawling.Crawler(temp[1])
			index += 1
			if len(crawResult) != 0:
				rndIndex.append(rnd)
				sym.append(key)
				r.append(crawResult)
			else:
				removeKey.append(key)
				continue
		except:
			return render_template('project1.html')
	# 결과값 없는 Diction 정리
	for i in range(len(removeKey)):
		del Diction[removeKey[i]]
	# 병원 정보 정리
	hospInformations = []
	# 받아온 지도 결과 값 출력
	for i in range(len(r)):
		hospInformations.append(r[i][rndIndex[i]][:4])
		print(hospInformations[i])
	p = []
	n = []
	try:
		for i in range(len(r)):
			tempP, tempN = kakaoMap.reviewAnalysis(hospInformations[i][1])
			print(tempP, tempN)
			p.append(tempP)
			n.append(tempN)
	except:
		sentence = "분석할 리뷰가 부족합니다."
		p.append(sentence)
		n.append(sentence)
	print(p)
	print(n)
	for i in range(len(p)):
		print("p", i, p[i])
	for i in range(len(n)):
		print("n", i, n[i])
	# 증상, 경도, 위도 넣는 리스트
	temp_map = []
	for row in range(len(r)):
		i = 0
		xy = []
		for col in range(len(r[row])):
			xy.append([sym[row], r[row][col][4][0], r[row][col][4][1]])
			i += 1
			if i > 0:
				break
		print("xy: ", xy)
		temp_map.append(xy)
	# return 값 리스트
	# Diction - 예상증상
	# XY - 병원 위도, 경도
	# hospInformations - 병원 위치 정보들
	kakao_key = "97c23c3cc66e3885bde6a88ecdcbd7be"
	return render_template('project_2.html', kakao_key = kakao_key, contents=Diction , XY = temp_map, hospInfo=hospInformations, pos = p, neg = n)

if __name__ == '__main__':
	app.run(host = "127.0.0.1:5000")