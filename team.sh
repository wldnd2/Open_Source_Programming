#!/bin/bash

read -p "루트 권한 패스워드를 입력해주세요 : " PW

wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
echo "$PW" | sudo -kS apt install ./google-chrome-stable_current_amd64.deb
google-chrome --version


echo "$PW" | sudo -kS apt install software-properties-common

pip install --upgrade pip
pip install webdriver-manager
pip3 install requests
pip3 install beautifulsoup4
pip3 install konlpy
pip3 install pandas
pip3 install matplotlib
pip3 install Blueprint
pip3 install selenium
pip3 install seaborn
pip3 install sklearn

cd
cd elasticsearch-8.2.0
./bin/elasticsearch -d
cd
cd Open_Source_Programming

chmod 700 geckodriver
chmod +x app.py

google-chrome http://127.0.0.1:5000/
python3 app.py

