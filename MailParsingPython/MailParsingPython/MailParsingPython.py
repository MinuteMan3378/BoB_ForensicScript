import datetime
import string
import os
import unicodecsv as csv
import sys
import codecs
import gmail
import httplib
import urllib
import urlparse
import cStringIO
import re
import hashlib
import exifread
import PIL

from gmail import Gmail
from io import BytesIO

today=str(datetime.datetime.now())[:10]
dirpath = os.path.expanduser('~') + '\Desktop\\result\\' + today 



def MD5(fName):
    hashMD5 = hashlib.md5()
    with open(fName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashMD5.update(chunk)
    return hashMD5.hexdigest()

def SHA1(fName):
    hashSHA1 = hashlib.sha1()
    with open(fName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashSHA1.update(chunk)
    return hashSHA1.hexdigest()

def todayDir() :    
    if os.path.isdir(dirpath) :
        print "[*] Today's directory already exists."
    else : 
        print "[*] Initializing directory..."
        os.makedirs(dirpath)

def unshortURL(url):
    parsed = urlparse.urlparse(url)
    h = httplib.HTTPConnection(parsed.netloc)
    h.request('HEAD', parsed.path)
    response = h.getresponse()
    if response.status/100 == 3 and response.getheader('Location'):
        return response.getheader('Location')
    else:
        return url

def makeCsv() :

    csvpath = dirpath+"\\result.csv"
    c = csv.writer(open(csvpath, "wb"))
    num="연번"
    time="시각"
    sURL="Shortened URL"
    fURL="Full URL"
    fName="파일명"
    lat="위도"
    lon="경도"
    MD5="MD5"
    SHA1="SHA1"
    list = (num, time, sURL, fURL, fName, lat, lon, MD5, SHA1)
    c = c.writerow(list)

def addCsv(filepath, n, t, sU, fU, fN, flat, flon, fMD5, fSHA1):
    csvpath = dirpath+"\\result.csv"
    c = csv.writer(open(csvpath, "wb"))
    num = n
    time = t
    sURL = sU
    fURL = fU
    fName = fN
    lat = flat
    lon = flon
    MD5 = fMD5
    SHA1 = fSHA1
    list = (num, time, sURL, fURL, fName, lat, lon, MD5, SHA1)
    c = c.writerow(list)

def readMail():
    try:
        
        g = Gmail()
        g = gmail.login('pshbob5th@gmail.com', 'qaz123ws')
        print "[*] Authentication complete."
        emails = g.inbox().mail(sender='imw3378@gmail.com')
        print "[*] Engaging email parsing."
        index = 1
        for email in emails:
            email.read()
            email.fetch()
            time = email.sent_at
            surl = re.findall('(https?:\/\/\S+)', str(email.body))
            surl = str(surl)[2:-2] 

            furl = unshortURL(surl)
            filename = furl.split('/')[-1]
            filepath = dirpath+"\\"+filename
            file = urllib.urlopen(furl)
            file.close()
            urllib.urlretrieve(furl, filepath)
    
            fMD5 = MD5(filepath)
            fSHA1 = SHA1(filepath)
            if filepath.split('.')[-1] == 'jpg' :
                
            index+=index+1
        

    except gmail.AuthenticationError:
        print "Auth fail"
    print "[*] Mail read complete."

   
todayDir()
makeCsv()
readMail()

