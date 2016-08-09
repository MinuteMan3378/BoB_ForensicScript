#-*- coding:utf-8 -*-
import datetime
import string
import os
import csv
import sys
import gmail
import httplib
import urllib
import urllib2
import urlparse
import re
import hashlib
import base64
import sqlite3
import ssl
import PIL
import requests

from PIL import Image
from PIL.ExifTags import TAGS, GPSTAGS
from cStringIO import StringIO
from gmail import Gmail
from io import BytesIO

def SQLTotalMap():
    finaldata = ""
    dirpath = os.path.expanduser('~') + '\Desktop\\result\\'
    conn = sqlite3.connect(os.path.expanduser('~') + '\Desktop\\result\\PSHPython.sqlite')
    cur = conn.cursor()
    sql = 'select MAX(idx) from PSH_homework'
    cur.execute(sql)
    row = cur.fetchall()
    row =  row[0][0]
    for i in range(row):
        i=i+1
        print i
        sql = 'select Latitude, Longitude from PSH_homework where idx = '+str(i)
        cur.execute(sql)
        row = cur.fetchall()
        lat, lon = row[0][0], row[0][1]
        print lat, lon
        if lon != "N/A" and lat != "N/A" :
            finaldata = finaldata+str(lat)+","+str(lon)+"|"
            print finaldata
    url = "http://maps.googleapis.com/maps/api/staticmap?autoscale=false&size=800x800&markers=color:red|"+finaldata+"&maptype=hybrid&key=AIzaSyDV5MU2pNXqkRXT_UooYqJdxM-Ytb7Perg"
    buffer = StringIO(urllib.urlopen(url).read())
    image = Image.open(buffer).convert('RGB')
    image.save(dirpath+"PSH_TOTALMAP.png")
        
        
def SQLInit(): # Make a sqlite db file if it's not exists
    if os.path.isfile(os.path.expanduser('~') + '\Desktop\\result\\PSHPython.sqlite') == False:
        conn = sqlite3.connect(os.path.expanduser('~') + '\Desktop\\result\\PSHPython.sqlite')
        cur = conn.cursor()
        sql = "create table PSH_homework(idx integer PRIMARY KEY not null, time varchar(32), Short_URL varchar(64), Full_URL varchar(512), File_name varchar(256), Latitude varchar(32), Longitude varchar(32), MD5 varchar(128), SHA1 varchar(128))"
        cur.execute(sql)
        conn.close()
        print "[*] Database initialized."

def SQLDump(time, sURL, fURL, fName, flat, flon, MD5, SHA1): # Add data to sqlite db    
    conn = sqlite3.connect(os.path.expanduser('~') + '\Desktop\\result\\PSHPython.sqlite')
    time = time.decode('utf-8')
    sURL = sURL.decode('utf-8')
    fURL = fURL.decode('utf-8')
    fName = fName.decode('utf-8')
    flat = flat.decode('utf-8')
    flon = flon.decode('utf-8')
    MD5 = MD5.decode('utf-8')
    SHA1 = SHA1.decode('utf-8')
    sql = 'insert into PSH_homework (time, Short_URL, Full_URL, File_name, Latitude, Longitude, MD5, SHA1) values ("'+time+'", "'+sURL+'", "'+fURL+'", "'+fName+'", "'+flat+'", "'+flon+'", "'+MD5+'", "'+SHA1+'")'
    conn.execute(sql)
    conn.commit()
    print "[*] Data added to table"
    conn.close()

def GPSMAP(filepath, gpsdata): # Generating map image, using Google Static Map API
    url = "http://maps.googleapis.com/maps/api/staticmap?autoscale=false&size=800x800&markers=color:red|"+gpsdata+"&maptype=hybrid&key=AIzaSyDV5MU2pNXqkRXT_UooYqJdxM-Ytb7Perg"
    buffer = StringIO(urllib.urlopen(url).read())
    image = Image.open(buffer).convert('RGB')
    image.save(dirpath+"\\"+today+"_GPSMAP.jpg")

def seperateGPSMAP(filepath, lat, lon): # Generating map image, using Google Static Map API
    url = "http://maps.googleapis.com/maps/api/staticmap?autoscale=false&size=800x800&markers=color:red|"+str(lat)+","+str(lon)+"|&maptype=hybrid&key=AIzaSyDV5MU2pNXqkRXT_UooYqJdxM-Ytb7Perg"
    buffer = StringIO(urllib.urlopen(url).read())
    image = Image.open(buffer).convert('RGB')
    image.save(dirpath+"\\"+today+"_SEP_GPSMAP.jpg")

def get_exif_data(image): #Getting EXIF data from image
    exif_data = {}
    info = image._getexif()
    if info:
        for tag, value in info.items():
            decoded = TAGS.get(tag, tag)
            if decoded == "GPSInfo":
                gps_data = {}
                for t in value:
                    sub_decoded = GPSTAGS.get(t, t)
                    gps_data[sub_decoded] = value[t]

                exif_data[decoded] = gps_data
            else:
                exif_data[decoded] = value

    return exif_data

def _get_if_exist(data, key):
    if key in data:
        return data[key]
		
    return None
	
def _convert_to_degress(value):
    d0 = value[0][0]
    d1 = value[0][1]
    d = float(d0) / float(d1)

    m0 = value[1][0]
    m1 = value[1][1]
    m = float(m0) / float(m1)

    s0 = value[2][0]
    s1 = value[2][1]
    s = float(s0) / float(s1)

    return d + (m / 60.0) + (s / 3600.0)

def get_lat_lon(exif_data): #Getting GPS data from EXIF data
    lat = None
    lon = None

    if "GPSInfo" in exif_data:		
        gps_info = exif_data["GPSInfo"]

        gps_latitude = _get_if_exist(gps_info, "GPSLatitude")
        gps_latitude_ref = _get_if_exist(gps_info, 'GPSLatitudeRef')
        gps_longitude = _get_if_exist(gps_info, 'GPSLongitude')
        gps_longitude_ref = _get_if_exist(gps_info, 'GPSLongitudeRef')

        if gps_latitude and gps_latitude_ref and gps_longitude and gps_longitude_ref:
            lat = _convert_to_degress(gps_latitude)
            if gps_latitude_ref != "N":                     
                lat = 0 - lat

            lon = _convert_to_degress(gps_longitude)
            if gps_longitude_ref != "E":
                lon = 0 - lon

    return lat, lon

def b64(txt): # Decode string if it's Base64    
    try:
        txt = str(txt.replace('\n', ' ').replace('\r', ''))
        rawtxt = base64.b64decode(txt)
        return rawtxt
    except:
        return txt       

def jpgGPS(imagepath): # Getting GPS data from image
    image = Image.open(imagepath)
    exif_data = get_exif_data(image)
    return get_lat_lon(exif_data)

def MD5(fName): # Hash the image(MD5)
    hashMD5 = hashlib.md5()
    with open(fName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashMD5.update(chunk)
    return hashMD5.hexdigest()

def SHA1(fName): # Hash the image(SHA1)
    hashSHA1 = hashlib.sha1()
    with open(fName, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hashSHA1.update(chunk)
    return hashSHA1.hexdigest()

def todayDir() : # Make today's directory   
    if os.path.isdir(dirpath) :
        print "[*] Today's directory already exists."
    else : 
        print "[*] Directory initialized."
        os.makedirs(dirpath)

def unshortURL(url): # Unshort given url
    while True :
        try:
            req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0' })
            req.add_header('Accept', 'application/json')
            res = urllib2.urlopen(req)
            
        except urllib2.HTTPError as err:
            if err.code == 404 :
                print "[*][*] 404 Error"
                url = url[:-1]
            else:
                url = url[:-1]
        else:
            break
    
    res = urllib2.urlopen(req)
    finalurl = res.geturl()
    return finalurl, url

def makeCsv() : # Make today's CSV file
    csvpath = dirpath+"\\result.csv"
    c = csv.writer(open(csvpath, "wb"))
    num=u"연번"
    time=u"시각"
    sURL="Shortened URL"
    fURL="Full URL"
    fName=u"파일명"
    lat=u"위도"
    lon=u"경도"
    MD5="MD5"
    SHA1="SHA1"
    list = (num.encode("cp949"), time.encode("cp949"), sURL, fURL, fName.encode("cp949"), lat.encode("cp949"), lon.encode("cp949"), MD5, SHA1)
    c = c.writerow(list)

def addCsv(filepath, n, t, sU, fU, fN, flat, flon, fMD5, fSHA1): # Add data to CSV file
    csvpath = dirpath+"\\result.csv"
    c = csv.writer(open(csvpath, "ab"))
    num = n.decode('utf-8')
    time = t.decode('utf-8')
    sURL = sU.decode('utf-8')
    fURL = fU.decode('utf-8')
    fName = fN.decode('utf-8')
    lat = flat.decode('utf-8')
    lon = flon.decode('utf-8')
    MD5 = fMD5.decode('utf-8')
    SHA1 = fSHA1.decode('utf-8')
    list = (num.encode("cp949"), time.encode("cp949"), sURL.encode("cp949"), fURL.encode("cp949"), fName.encode("cp949"), lat.encode("cp949"), lon.encode("cp949"), MD5, SHA1)
    c = c.writerow(list)

def readMail(): # Read & Parse the mail
    index = 0
    gpsflag = 0

    seplat = 0.0
    maxlat = 0.0
    minlat = 999.999
    datalat = []


    seplon = 0.0
    maxlon = 0.0
    minlon = 999.999
    datalon = []
    gpsdata = ""
    try:       
        flat = "N/A"
        flon = "N/A"
        g = Gmail()
        g = gmail.login('pshbob5th@gmail.com', 'qaz123ws')
        print "[*] Authentication complete."
        emails = g.inbox().mail(sender='fl0ckfl0ck@hotmail.com')
        
        print "[*] Engaging email parsing."
        for email in emails:
            index = index + 1
            email.read()
            email.fetch()
            time = email.sent_at
            print time
            time = time + datetime.timedelta(hours=9)
            print time
            body = email.body
            print "[*] RAW body : "+body
            if (len(body) >= 12) and (body.find("http") == -1) :
                body = b64(email.body)
                print "[*] Base64 decoded body : "+body
            surl = re.findall('(https?:\/\/\S+)', str(body))
            surl = str(surl)[2:-2]
            path = (surl.split("/")[-1])
            surl = surl.replace(path, '')
            path = re.sub('[=@#?$}.]', '', path.decode('utf-8'))
            surl = surl + path
            if len(str(surl).split("/")[-1]) > 4 and str(surl).find("grep.kr") != -1 :
               print str(surl.find("grep.kr"))
               path = (surl.split("/")[-1])
               surl = surl.replace(path, '')
               path = path[:4]
               surl = surl + path
               print "[*] grep.kr processed: ", surl
            if str(surl).decode('utf-8').find(str("\\x")) > -1 :
                print surl
                print str(surl).decode('utf-8')
                surl = re.sub('(\\\\x..)', '', str(surl).decode('utf-8'))                
                print "[*] Junk data removed: ", surl
            if str(surl).find('\\n') != -1:
                surl = str(surl)[:-2]
                print "[*] New line removed: ", surl
            furl, surl = unshortURL(surl.decode('utf-8'))            
            print "[*] URL Unshortened"
            print "[*] Shortened URL : "+surl
            print "[*] Full URL : "+str(urllib.unquote(urllib.unquote(furl)).decode('utf-8').encode('cp949'))
            filename = furl.split('/')[-1]
            filepath = (dirpath+"\\"+filename)
            filepath =  urllib2.unquote(urllib.unquote(filepath)).decode('utf-8').encode('cp949')
            req = urllib2.Request(furl, headers={ 'User-Agent': 'Mozilla/5.0' })
            req.add_header('Accept', 'application/json')
            file = urllib2.urlopen(req)
            file.close()
            urllib.urlretrieve(furl, filepath)
            
            fMD5 = MD5(filepath)
            fSHA1 = SHA1(filepath)
            if filepath.split('.')[-1] == 'jpg' :                         
                flat, flon = jpgGPS(filepath)
                if flat!="N/A" and flon!="N/A" :
                    print "[*] GPS data found, Lat: " + str(flat) +" Lon:"+str(flon)
                    flat = float(flat)
                    flon = float(flon)
                    datalat.append(flat)
                    datalon.append(flon)               
                    if(flat > maxlat) :
                        maxlat = flat
                    if(flat < minlat) :
                        minlat = flat
                    if(flon > maxlon) :
                        maxlon = flon
                    if(flon < minlon) :
                        minlon = flon                   
                    gpsflag=1
                    
            
            furl = urllib.unquote(urllib.unquote(furl))
            filename = urllib.unquote(urllib.unquote(filename))
            print "[*] Information added to CSV file"
            addCsv(filepath, str(index), str(time), str(surl), str(furl), str(filename), str(flat), str(flon), str(fMD5), str(fSHA1))
            SQLDump(str(time), str(surl), str(furl), str(filename), str(flat), str(flon), str(fMD5), str(fSHA1))      
        finallat = datalat[:]      
        finallon = datalon[:]
    except gmail.AuthenticationError:
        print "Auth fail"
    print "[*] Mail read complete."
    if gpsflag == 1:
        latsum = 0.0
        lonsum = 0.0
        for i in datalat:
            latsum = latsum + i
        latavg = latsum / len(datalat)
        for i in datalon:
            lonsum = lonsum + i
        lonavg = lonsum / len(datalon)
        if((abs(maxlat-minlat) > 1.5) or abs(maxlon-minlon) > 1.5) and ((abs(latavg-minlat) > 1.5) or (abs(lonavg-minlon) > 1.5)) :
            datalat.remove(maxlat)
            datalat.remove(minlat)
            datalon.remove(maxlon)
            datalon.remove(minlon)
            sum = 0.0
            latsum = 0.0
            lonsum = 0.0
            print maxlat, minlat, latavg, datalat, finallat 
            print maxlon, minlon, lonavg, datalon, finallon
            
            print lonavg
            if(abs(latavg-minlat) > 1.5):
                print "[*] latavg - minlat : ",latavg-minlat
                finallat.remove(minlat)
                seplat = minlat
            elif(abs(maxlat-latavg) > 1.5) :
                print "[*] maxlat - latavg : ", maxlat-latavg
                finallat.remove(maxlat)
                seplat = maxlat
            if(abs(maxlon-lonavg) > 1.5) :
                print "[*] maxlon - lonavg : ", maxlon-lonavg
                finallon.remove(maxlon)
                seplon = maxlon
            elif(abs(lonavg-minlon) > 1.5):
                print "[*] lonavg - minlon : ",lonavg-minlon
                finallon.remove(minlon)
                seplon = minlon
            
            seperateGPSMAP(filepath, seplat, seplon)
            print seplat, seplon
        for i in range(len(finallat)):
            gpsdata = gpsdata+str(finallat[i])+","+str(finallon[i])+"|"
        GPSMAP(filepath, gpsdata)
   

ssl._create_default_https_context = ssl._create_unverified_context
opener = urllib2.build_opener(urllib2.HTTPSHandler(context=ssl.SSLContext(ssl.PROTOCOL_SSLv23)))
urllib2.install_opener(opener)
today=str(datetime.datetime.now())[:10] # YYYY MM DD for name of directory
year = today[:4]
month = today[5:7]
day = today[-2:]
dirpath = os.path.expanduser('~') + '\Desktop\\result\\' + today # Path of directory
ctx = ssl.create_default_context()
ctx.check_hostname = False
ctx.verify_mode = ssl.CERT_NONE
flat = "N/A"
flon = "N/A"
g = Gmail()
g = gmail.login('pshbob5th@gmail.com', 'qaz123ws')
print "[*] Authentication complete."
emails = g.inbox().mail(sender='fl0ckfl0ck@hotmail.com')
        
print "[*] Engaging email parsing."
for email in emails:
        email.read()
        email.fetch()
        time = email.sent_at
        print email.subject
        print "original time: ",time
        time = time + datetime.timedelta(hours=9)
        print "processed time: ",time
        print "________________\r\n"
todayDir()
SQLInit()
makeCsv()
readMail()

