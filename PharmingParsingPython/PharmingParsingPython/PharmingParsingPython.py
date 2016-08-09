# -*- coding: utf-8 -*-

import os
import sys
import urllib
import urllib2
import re
import base64
import requests
import zipfile


url = "http://knpu.co.kr/pharming/"

certnum = 0 # 인증서 갯수   
victim = {} # 피해자와 해당하는 피해 금액. [피해자 이름]:[피해 액수 합]
victimCert = {} # 피해자와 인증서 피해. [피해자 이름]:[인증서 피해량]
bankCert = {} # 은행과 인증서 피해. [은행 이름]:[인증서 피해량]
bankname = "" # 은행 이름 변수
victimname = "" # 피해자 이름 변수
totalMoney = 0 # 피해 액수 총합 변수
unstolen = {} # 무 피해 인원. [대상자 이름]:1

def b64(txt): # Base64 디코더  
    try:
        txt = str(txt.replace('\n', ' ').replace('\r', ''))
        rawtxt = base64.b64decode(txt)
        return rawtxt
    except:
        return txt

dfFile = open("C:\\Users\\Snag\\Documents\\BoB\\dflist.txt", "rb") # 디포트랙 교육생 이름
line = dfFile.readline() # 파일 열기
while line:
    victim[line[:-2]] = 0 # victim 딕셔너리에 이름 채워넣기
    victimCert[line[:-2]] = 0 # victimCert 딕셔너리에 이름 채워넣기
    line = dfFile.readline() # 새로 한 줄 읽기
dfFile.close() # 파일 닫기

idxFile = open("C:\\Users\\Snag\\Documents\\BoB\\Indexof_pharming.txt", "rb") # zip 파일 이름
line = idxFile.readline() # 파일 열기
while line:
    filename = re.findall('(^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.zip)', line)
    # 파일 이름 목록에서 정규식으로 긁어오기
    filename = str(filename)[2:-2] # 리스트 문자("[, ]") 떼어내서 파일 이름 만들기
    filepathname = filename[:-3] # zip 떼어내서 폴더 이름 만들기
    furl = url+filename # 파일 다운로드 받을 주소 제작
    dirpath = "C:\\Users\\Snag\\Documents\\BoB\\cert\\"+filepathname # 압축이 풀릴 폴더 이름
    filepath = "C:\\Users\\Snag\\Documents\\BoB\\cert\\"+filename # 다운로드 받은 파일이 저장될 경로

    if not os.path.isfile(filepath) : # 파일이 존재하지 않으면
        req = urllib2.Request(furl, headers={ 'User-Agent': 'Mozilla/5.0' })
        req.add_header('Accept', 'application/json')
        file = urllib2.urlopen(req) # 연결해서
        file.close()
        urllib.urlretrieve(furl, filepath) # 받아오기

    zip_ref = zipfile.ZipFile(filepath, 'r') # 압축 파일 읽어오고
    zip_ref.extractall(dirpath) # 압축 풀고
    zip_ref.close() # 압축 파일 닫고

    for (dirp, dirn, filenames) in os.walk(dirpath): # 디렉토리 경로 읽어서
        if str(filenames).find(".cert") != -1: # 하위 파일 중에 .cert가 있으면
            money=0 # 피해 금액 변수
            filename = filenames[0] # 파일 이름 처리
            certnum = certnum + 1 # 인증서 피해량 + 1
            certfile = open(dirp+"\\"+filename, "rb") # 인증서 파일 열고
            certline = certfile.readline() # 한 줄 읽기

            try:
                certcon = int(str(b64(certline)).decode('utf-8')[9:-5]) 
                # 인증서 내용 읽어서 b64 디코드 하고 숫자만 뽑아내서
                money = certcon # 피해 금액 변수에 대입
            except:
                pass # 오류 나면 패스

            filename = filename.split("\\")[-1] # 인증서 파일 이름 변수
            filename = str(filename)[2:-2]  # 리스트 문자("[, ]") 떼어내서 파일 이름 만들기
            victimname = filename.replace("cn=", '') # 피해자 이름 변수에 대입
            victimname = filename.split(",")[0]
            victimname = victimname[1:]
            bankname = filename.replace("ou=", '') # 은행 이름 변수에 대입            
            bankname = filename.split(",")[1]
            bankname = bankname[3:]
            
            if bankname in bankCert: # 은행:인증서 딕셔너리에 읽어온 은행 이름이 있으면
               bankCert[bankname] += 1 # 해당 은행 인증서 피해량 + 1
            else : # 없으면
               bankCert[bankname] = 1 # 해당 은행 생성, 인증서 피해량 + 1

            if victimname in victimCert: # 피해자:인증서 딕셔너리에 읽어온 피해자 이름이 있으면
                victimCert[victimname] += 1 # 피해자 인증서 피해량 + 1
            else : # 없으면
                victimCert[victimname] = 1 # 해당 피해자 생성, 인증서 피해량 +1

            if victimname in victim: # 피해자:금액 딕셔너리에 읽어온 피해자 이름이 있으면
                victim[victimname] += money # 피해 금액 + 피해량
            else : # 없으면
                victim[victimname] = money # 새로 대입
             
    line = idxFile.readline() # 새로 한 줄 읽기
idxFile.close() # 파일 닫기

print "[*] 총 인증서 피해: "+"{:,}".format(certnum)+"개"

for key, value in victim.iteritems(): # victim 딕셔너리에서 key와 value 하나씩 불러오기
    totalMoney = totalMoney + int(value) # 최종 피해 금액 합산

print "[*] 총 피해 액수: "+"{:,}".format(totalMoney)+"(만원)" 
print "------------------------------------------------------------"
for key, value in victim.iteritems(): # 피해자:금액 딕셔너리에서 key와 value 하나씩 불러오기
    if value != 0 : # 피해 금액이 0이 아니면
        print "[*] 피해자 이름: "+str(key)+", 피해 금액: "+"{:,}".format(value)+"(만원)"
    else : # 피해 금액이 0이면
        unstolen[key] = 1  # 무 피해 딕셔너리에 등록  

print "------------------------------------------------------------"
for key, value in victimCert.iteritems(): # 피해자:인증서 딕셔너리에서 key와 value 하나씩 불러오기
    if value != 0 : # 인증서 피해량이 0이 아니면
            print "[*] 피해자 이름: "+str(key)+", 인증서 피해: "+"{:,}".format(value)
    else : # 인증서 피해량이 0이면
        unstolen[key] = 1

print "------------------------------------------------------------"
for key, value in bankCert.iteritems(): # 은행:인증서 딕셔너리에서 key와 value 하나씩 불러오기
    print "[*] 은행 이름: "+str(key)+", 인증서 피해: "+"{:,}".format(value)

print "------------------------------------------------------------"
for key, value in unstolen.iteritems(): # 무 피해 딕셔너리에서 key와 value 하나씩 불러오기
    print "[*] 무 피해: ", key