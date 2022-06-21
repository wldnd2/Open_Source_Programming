#!/bin/bash

pip install --upgrade pip
pip install webdriver-manager
pip3 install elasticsearch
pip3 install requests
pip3 install beautifulsoup4
pip3 install konlpy
pip3 install pandas
pip3 install matplotlib
pip3 install Blueprint
pip3 install selenium
pip3 install seaborn
pip3 install sklearn

chmod +x execute.sh
gnome-terminal -e ./execute.sh
cd ..
cd elasticsearch-8.2.0
./bin/elasticsearch
echo "elasticsearch!!!!!!!!!!!!!!!"
curl -XDELETE localhost:9200/*


