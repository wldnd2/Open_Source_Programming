#!/usr/bin/python
#-*- coding: utf-8 -*-

import sys
import re
import requests
from bs4 import BeautifulSoup
from elasticsearch import Elasticsearch
from urllib.request import urlopen

def head_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    head_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of head_symptoms: ", len(head_symptoms))
    print(head_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of head_symptoms: ", len(head_symptoms))
    res_links=[] #result links
    for idx in head_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("head_symptoms keys: ", len(head_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = head_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            head_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    print("num Of each symtoms: ", len(each_symp_data))
    dict_of_head_symptons = dict()
    
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in head_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = head_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', head_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_head_symptons[head_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_head_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="head_symptons", document=dict_of_head_symptons)
    
    if symptom not in dict_of_head_symptons.keys():
        return {}
    return dict_of_head_symptons[symptom]
    
def chest_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000020"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    chest_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of chest_symptoms: ", len(chest_symptoms))
    print(chest_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of chest_symptoms: ", len(chest_symptoms))
    res_links=[] #result links
    for idx in chest_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("chest_symptoms keys: ", len(chest_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = chest_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            chest_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1
    dict_of_chest_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in chest_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = chest_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', chest_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_chest_symptons[chest_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_chest_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="chest_symptons", document=dict_of_chest_symptons)
    if symptom not in dict_of_chest_symptons.keys():
        return {}
    return dict_of_chest_symptons[symptom]
    

def arm_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000018"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    arm_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of arm_symptoms: ", len(arm_symptoms))
    print(arm_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of arm_symptoms: ", len(arm_symptoms))
    res_links=[] #result links
    for idx in arm_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("arm_symptoms keys: ", len(arm_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = arm_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            arm_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1
    dict_of_arm_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in arm_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = arm_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', arm_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_arm_symptons[arm_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_arm_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="arm_symptons", document=dict_of_arm_symptons)
    if symptom not in dict_of_arm_symptons.keys():
        return {}
    return dict_of_arm_symptons[symptom]
    


def back_symtoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000006"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    back_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of back_symptoms: ", len(back_symptoms))
    print(back_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of back_symptoms: ", len(back_symptoms))
    res_links=[] #result links
    for idx in back_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("back_symptoms keys: ", len(back_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = back_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            back_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    dict_of_back_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in back_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = back_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', back_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_back_symptons[back_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_back_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="back_symptons", document=dict_of_back_symptons)
    if symptom not in dict_of_back_symptons.keys():
        return {}
    return dict_of_back_symptons[symptom]
    

def hip_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000013"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    hip_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of hip_symptoms: ", len(hip_symptoms))
    print(hip_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of hip_symptoms: ", len(hip_symptoms))
    res_links=[] #result links
    for idx in hip_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("hip_symptoms keys: ", len(hip_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = hip_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            hip_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    dict_of_hip_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in hip_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = hip_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', hip_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_hip_symptons[hip_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_hip_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="hip_symptons", document=dict_of_hip_symptons)
    if symptom not in dict_of_hip_symptons.keys():
        return {}
    return dict_of_hip_symptons[symptom]
    

def leg_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000005"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    leg_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of leg_symptoms: ", len(leg_symptoms))
    print(leg_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of leg_symptoms: ", len(leg_symptoms))
    res_links=[] #result links
    for idx in leg_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("leg_symptoms keys: ", len(leg_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = leg_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            leg_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    dict_of_leg_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in leg_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = leg_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', leg_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_leg_symptons[leg_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_leg_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="leg_symptons", document=dict_of_leg_symptons)
    if symptom not in dict_of_leg_symptons.keys():
        return {}
    return dict_of_leg_symptons[symptom]
    

def neck_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000008"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    neck_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of neck_symptoms: ", len(neck_symptoms)) 
    print(neck_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of neck_symptoms: ", len(neck_symptoms))
    res_links=[] #result links
    for idx in neck_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("neck_symptoms keys: ", len(neck_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = neck_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            neck_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    dict_of_neck_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in neck_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = neck_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', neck_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_neck_symptons[neck_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_neck_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="neck_symptons", document=dict_of_neck_symptons)
    if symptom not in dict_of_neck_symptons.keys():
        return {}
    return dict_of_neck_symptons[symptom]
    

def stomach_symptoms(symptom):
    url = "https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomSubmain.do?partId=B000010"
    res = requests.get(url)
    soup = BeautifulSoup(res.content, "html.parser")
    #find and store symptom_def_urls
    symptom_link_data=soup.find("div", {"class":"searchCont"}).find_all('a')
    symptom_def_urls=[]
    for i in range(len(symptom_link_data)):
        link=symptom_link_data[i].get('href')
        symptom_def_urls.append('https://www.amc.seoul.kr'+link)
    #sympton names
    symptom_names=[]
    for i in range(len(symptom_link_data)):
        name=symptom_link_data[i].get_text()
        symptom_names.append(name)
    #sympton ids
    symptom_ids=[]
    for i in range(len(symptom_link_data)):
        id_name="cont1_"+str(i+1)
        symptom_id=soup.find("input", {'id':id_name}).get('value')
        symptom_ids.append(symptom_id)
    #dictionariation
    stomach_symptoms = dict(zip(symptom_ids, symptom_names))#symptom_ids = SSxxxxxxxxxx, symptom_names = 'xxxx', head_symptoms = dictionary
    print("length of stomach_symptoms: ", len(stomach_symptoms))
    print(stomach_symptoms)


    #SAVE links of causes of symptoms of heads
    print("length of stomach_symptoms: ", len(stomach_symptoms))
    res_links=[] #result links
    for idx in stomach_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    i=0


    print("stomach_symptoms keys: ", len(stomach_symptoms.keys()))
    each_symp_data=[] #data of each symptons
    keys = stomach_symptoms.copy().keys()
    print("get keys")
    for idx in keys:
        print(idx, end=' ')
        res=requests.get(res_links[i])     # 추린 내용
        soup=BeautifulSoup(res.content, "html.parser") 
    
        contentId_link_data=[]
        res_names=[]
        # symptom result link의 상세 정보
        symptom_res_link_data=soup.body.find_all(class_="contTitle")
    
        if len(symptom_res_link_data) == 0:
            stomach_symptoms.pop(idx)
            i += 1
            continue
        for j in range(len(symptom_res_link_data)):
            res_names.append(symptom_res_link_data[j].getText().strip())
        each_symp_data.append(res_names)
        i=i+1

    dict_of_stomach_symptons = dict()
    import re

    i=0
    detail_info_list=[]   # 세부 정보
    for idx in stomach_symptoms:
        res_link='https://www.amc.seoul.kr/asan/healthinfo/symptom/symptomList.do?searchFrmPartId=B000007&symptomIds='+idx
        res_links.append(res_link)

    keys = stomach_symptoms.copy().keys()
    for idx in keys:
        sympt_res_html=requests.get(res_links[i])     # 추린 내용
        sympt_res_Object=BeautifulSoup(sympt_res_html.content, "html.parser")
        print('선택된 증상 이름: ', stomach_symptoms[idx])   
    
        each_symp_data=[]     # 증상별 data
        res_names=[]
    
        # symptom result link의 상세 정보
        symptom_res_link_data=sympt_res_Object.body.find_all(class_="contTitle")
        # print(symptom_res_link_data)
    
        causes_with_dpartment = dict()
        for j in range(len(symptom_res_link_data)):
            one_disease_data=[]
        
            res_names.append(symptom_res_link_data[j].get_text().strip())  # 예상 질병 이름 모으기
            #one_disease_data.append({"질병 이름":symptom_res_link_data[j].get_text().strip()})
            # print("질병 이름:", symptom_res_link_data[j].get_text().strip())
        
            contentId=symptom_res_link_data[j].find('a').get('href')
            res_link_symp='https://www.amc.seoul.kr'+contentId
            sympt_res_html2=requests.get(res_link_symp)     # 추린 내용

            sympt_res_Object2=BeautifulSoup(sympt_res_html2.content, "html.parser")
        
            # 진료과 관련 정보
            department_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dd')
            department_idx_datas=sympt_res_Object2.body.find("div", {"class":"contBox"}).find_all('dt')
        
            # 진료과
            for depart_idx in range(len(department_datas)):
                if department_idx_datas[depart_idx].get_text().strip()=="진료과":
                    dapartment_name=department_datas[depart_idx].get_text().replace(",", "")
                    dapartment_name_str=re.findall(r'\S+', dapartment_name)
                    one_disease_data.append(dapartment_name_str)
                

            cause = symptom_res_link_data[j].get_text().strip()
            if len(one_disease_data) > 0:
                causes_with_dpartment[cause] = one_disease_data[0]#dictionary key: causes, values: departments
                print(causes_with_dpartment)
            #each_symp_data.append(causes_with_dpartment)
        if len(causes_with_dpartment) > 0:
            dict_of_stomach_symptons[stomach_symptoms[idx]] = causes_with_dpartment
        print()
        i=i+1
    for key, value in dict_of_stomach_symptons.items():
        print(key, ": ", value)
    from elasticsearch import Elasticsearch
    import json
    es_host="http://localhost:9200"
    es = Elasticsearch(es_host)
    error = None
    es.index(index="stomach_symptons", document=dict_of_stomach_symptons)
    if symptom not in dict_of_stomach_symptons.keys():
        return {}
    return dict_of_stomach_symptons[symptom]
    




