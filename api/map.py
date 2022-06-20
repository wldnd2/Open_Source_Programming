from flask import Blueprint, jsonify,render_template, request #request 파라미터 받기
import requests #requests 다른 url로 요청 보내기

bp = Blueprint('main', __name__)

@bp.route("/", methods=['GET'])
def hello_world():
    location = request.args.get("address")
    url = f"https://dapi.kakao.com/v2/local/search/address.json?query={location}"
    kakao_key = "8d7127274d16ab32508bc7b4936be2d4" # 보안주의~
    result = requests.get(url, headers={"Authorization":f"KakaoAK {kakao_key}"}).json()
    if len(result['documents'])==0:
        return jsonify({'code':False})
    x = result['documents'][0]['x']
    y = result['documents'][0]['y']
    print(x,y)
    return jsonify({'code':True,'x':x,'y':y})

@bp.route("/print", methods=['GET'])
def map():#make this fuction to a fuction which take array for an input and then pass inf from mapcrawling
    location = request.args.get("address1")
    location2 = request.args.get("address2")
    result = requests.get(f"http://localhost:5000/map?address={location}").json()
    result2 = requests.get(f"http://localhost:5000/map?address={location2}").json();
    kakao_key = "7adda45551c9f749806e1321b9a045b5" # 보안주의~
    if result['code']==False or result['code']==False:
        return "해당 지역 없음"
    return ('<div id="map" style="width:500px;height:400px;"></div>'+
    f'<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={kakao_key}"></script>'+
    '<script>'+
        "var container = document.getElementById('map');"+
        'var options = {'+ 
            f"center: new kakao.maps.LatLng({(float(result['y'])+float(result2['y']))/2}, {(float(result['x'])+float(result2['x']))/2}),"+
            'level: 5'+
        '};'+
        'var map = new kakao.maps.Map(container, options);'+
        f"var markerPosition  = new kakao.maps.LatLng({result['y']}, {result['x']});"+ 
        'var marker = new kakao.maps.Marker({position: markerPosition});'+
        f"var markerPosition2  = new kakao.maps.LatLng({result2['y']}, {result2['x']});"+ 
        'var marker2 = new kakao.maps.Marker({position: markerPosition2});'+
        'marker.setMap(map);'+
        'marker2.setMap(map);'+
    '</script>')


from . import mapCrawling

@bp.route("/printAll",methods=['GET'])
def apiTest():
    result = mapCrawling.Crawler("정형외과")
    print(result)
    kakao_key = "7adda45551c9f749806e1321b9a045b5" # 보안주의~
    temp_map = ""
    i = 0
    for a in result:
        temp_map += render_template('map.html',i=i,x=a[4][0],y=a[4][1])
        i += 1
    return f'<script type="text/javascript" src="//dapi.kakao.com/v2/maps/sdk.js?appkey={kakao_key}"></script>'+temp_map