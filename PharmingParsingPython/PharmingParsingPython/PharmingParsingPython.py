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

certnum = 0 # ������ ����   
victim = {} # �����ڿ� �ش��ϴ� ���� �ݾ�. [������ �̸�]:[���� �׼� ��]
victimCert = {} # �����ڿ� ������ ����. [������ �̸�]:[������ ���ط�]
bankCert = {} # ����� ������ ����. [���� �̸�]:[������ ���ط�]
bankname = "" # ���� �̸� ����
victimname = "" # ������ �̸� ����
totalMoney = 0 # ���� �׼� ���� ����
unstolen = {} # �� ���� �ο�. [����� �̸�]:1

def b64(txt): # Base64 ���ڴ�  
    try:
        txt = str(txt.replace('\n', ' ').replace('\r', ''))
        rawtxt = base64.b64decode(txt)
        return rawtxt
    except:
        return txt

dfFile = open("C:\\Users\\Snag\\Documents\\BoB\\dflist.txt", "rb") # ����Ʈ�� ������ �̸�
line = dfFile.readline() # ���� ����
while line:
    victim[line[:-2]] = 0 # victim ��ųʸ��� �̸� ä���ֱ�
    victimCert[line[:-2]] = 0 # victimCert ��ųʸ��� �̸� ä���ֱ�
    line = dfFile.readline() # ���� �� �� �б�
dfFile.close() # ���� �ݱ�

idxFile = open("C:\\Users\\Snag\\Documents\\BoB\\Indexof_pharming.txt", "rb") # zip ���� �̸�
line = idxFile.readline() # ���� ����
while line:
    filename = re.findall('(^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}.zip)', line)
    # ���� �̸� ��Ͽ��� ���Խ����� �ܾ����
    filename = str(filename)[2:-2] # ����Ʈ ����("[, ]") ����� ���� �̸� �����
    filepathname = filename[:-3] # zip ����� ���� �̸� �����
    furl = url+filename # ���� �ٿ�ε� ���� �ּ� ����
    dirpath = "C:\\Users\\Snag\\Documents\\BoB\\cert\\"+filepathname # ������ Ǯ�� ���� �̸�
    filepath = "C:\\Users\\Snag\\Documents\\BoB\\cert\\"+filename # �ٿ�ε� ���� ������ ����� ���

    if not os.path.isfile(filepath) : # ������ �������� ������
        req = urllib2.Request(furl, headers={ 'User-Agent': 'Mozilla/5.0' })
        req.add_header('Accept', 'application/json')
        file = urllib2.urlopen(req) # �����ؼ�
        file.close()
        urllib.urlretrieve(furl, filepath) # �޾ƿ���

    zip_ref = zipfile.ZipFile(filepath, 'r') # ���� ���� �о����
    zip_ref.extractall(dirpath) # ���� Ǯ��
    zip_ref.close() # ���� ���� �ݰ�

    for (dirp, dirn, filenames) in os.walk(dirpath): # ���丮 ��� �о
        if str(filenames).find(".cert") != -1: # ���� ���� �߿� .cert�� ������
            money=0 # ���� �ݾ� ����
            filename = filenames[0] # ���� �̸� ó��
            certnum = certnum + 1 # ������ ���ط� + 1
            certfile = open(dirp+"\\"+filename, "rb") # ������ ���� ����
            certline = certfile.readline() # �� �� �б�

            try:
                certcon = int(str(b64(certline)).decode('utf-8')[9:-5]) 
                # ������ ���� �о b64 ���ڵ� �ϰ� ���ڸ� �̾Ƴ���
                money = certcon # ���� �ݾ� ������ ����
            except:
                pass # ���� ���� �н�

            filename = filename.split("\\")[-1] # ������ ���� �̸� ����
            filename = str(filename)[2:-2]  # ����Ʈ ����("[, ]") ����� ���� �̸� �����
            victimname = filename.replace("cn=", '') # ������ �̸� ������ ����
            victimname = filename.split(",")[0]
            victimname = victimname[1:]
            bankname = filename.replace("ou=", '') # ���� �̸� ������ ����            
            bankname = filename.split(",")[1]
            bankname = bankname[3:]
            
            if bankname in bankCert: # ����:������ ��ųʸ��� �о�� ���� �̸��� ������
               bankCert[bankname] += 1 # �ش� ���� ������ ���ط� + 1
            else : # ������
               bankCert[bankname] = 1 # �ش� ���� ����, ������ ���ط� + 1

            if victimname in victimCert: # ������:������ ��ųʸ��� �о�� ������ �̸��� ������
                victimCert[victimname] += 1 # ������ ������ ���ط� + 1
            else : # ������
                victimCert[victimname] = 1 # �ش� ������ ����, ������ ���ط� +1

            if victimname in victim: # ������:�ݾ� ��ųʸ��� �о�� ������ �̸��� ������
                victim[victimname] += money # ���� �ݾ� + ���ط�
            else : # ������
                victim[victimname] = money # ���� ����
             
    line = idxFile.readline() # ���� �� �� �б�
idxFile.close() # ���� �ݱ�

print "[*] �� ������ ����: "+"{:,}".format(certnum)+"��"

for key, value in victim.iteritems(): # victim ��ųʸ����� key�� value �ϳ��� �ҷ�����
    totalMoney = totalMoney + int(value) # ���� ���� �ݾ� �ջ�

print "[*] �� ���� �׼�: "+"{:,}".format(totalMoney)+"(����)" 
print "------------------------------------------------------------"
for key, value in victim.iteritems(): # ������:�ݾ� ��ųʸ����� key�� value �ϳ��� �ҷ�����
    if value != 0 : # ���� �ݾ��� 0�� �ƴϸ�
        print "[*] ������ �̸�: "+str(key)+", ���� �ݾ�: "+"{:,}".format(value)+"(����)"
    else : # ���� �ݾ��� 0�̸�
        unstolen[key] = 1  # �� ���� ��ųʸ��� ���  

print "------------------------------------------------------------"
for key, value in victimCert.iteritems(): # ������:������ ��ųʸ����� key�� value �ϳ��� �ҷ�����
    if value != 0 : # ������ ���ط��� 0�� �ƴϸ�
            print "[*] ������ �̸�: "+str(key)+", ������ ����: "+"{:,}".format(value)
    else : # ������ ���ط��� 0�̸�
        unstolen[key] = 1

print "------------------------------------------------------------"
for key, value in bankCert.iteritems(): # ����:������ ��ųʸ����� key�� value �ϳ��� �ҷ�����
    print "[*] ���� �̸�: "+str(key)+", ������ ����: "+"{:,}".format(value)

print "------------------------------------------------------------"
for key, value in unstolen.iteritems(): # �� ���� ��ųʸ����� key�� value �ϳ��� �ҷ�����
    print "[*] �� ����: ", key