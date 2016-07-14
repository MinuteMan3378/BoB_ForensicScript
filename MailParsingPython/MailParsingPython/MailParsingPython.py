# -*- coding: utf-8 -*-

import datetime
import string
import os
import csv
import sys
import codecs


today=str(datetime.datetime.now())[:10]
dirpath = os.path.expanduser('~') + '\Desktop\\' + today


def todayDir() :    
    if os.path.isdir(dirpath) :
        print "[*] Today's directory already exists"
    else : 
        os.mkdir(dirpath)

def makeCsv() :
    csvpath = dirpath+"\\result.csv"
    c = csv.writer(codecs.open(csvpath,"wb", encoding="utf-8"))
    c = c.writerow(["연번","시각","Shortened URL","Full URL","파일명","위도","경도","MD5","SHA1"])



todayDir()

makeCsv()

