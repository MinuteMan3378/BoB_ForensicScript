import os
import csv

filepath = "C:\\Users\\Snag\\Desktop\\E01\\direc.csv"
fNum = {}
fSizeSum = {}

def fCount(fName, fSize):
    fName = fName.split("\\")[-1].split(".")[-1].lower()   
    if fName.find("_") != -1: 
        fName = fName.split("_")[1].lower()
    if fName in fNum:
        fNum[fName] += 1
        fSizeSum[fName] += fSize
    else :
        fNum[fName] = 1
        fSizeSum[fName] = fSize

def fCSV():
    with open("C:\\Users\\Snag\\Desktop\\E01\\YKF1Result.csv", 'wb') as output:
        c = csv.writer(output)
        c.writerow(["Extension name", "Extension Count", "Average Size"])
        for key in fNum.iterkeys() :     
            fName = key
            fCnt = fNum[fName]
            fSizeAvg = int(fSizeSum[fName]) / int(fCnt)
            print fName, fCnt, fSizeAvg
            try:            
                c.writerow([str([fName]), fCnt, fSizeAvg])
            except:
                pass
        c.writerow(["All Extensions", len(fNum)])  
        
    
with open(filepath, 'rb') as input:
    for row in csv.reader((line.replace('\0','').replace('\t', ',') for line in input), delimiter=","):
        try:
            fName = row[1]
            fSize = row[2]
            if fSize != "" and fName[-1] != '\\':
                    fCount(str(fName), int(fSize))
        except:
            pass      

fCSV()
