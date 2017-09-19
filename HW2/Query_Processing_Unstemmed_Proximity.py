from __future__ import division
import string
from stemming.porter2 import stem
from string import digits
import re
import time
from Stemmed_Stopwords_Removed_Index import TermVector
from collections import OrderedDict
import dill

def unpickler(file):
    f = open(file, 'rb')
    ds = dill.load(f)
    f.close()
    return ds

def parseCatalog(file):
    catalog = {}
    catalogFile = open(file, 'r')
    for line in catalogFile.readlines():
        content = line.strip().split(',')
        catalog[content[0]] = content[1:]
    return catalog

def queryMaker():
    f = open('ProximityQueryModel.txt', 'r')
    queries = []
    for line in f:
        queries.append(re.sub('[\-\.\"\s]+', ' ', line).strip().translate(None, digits))
    return queries

def queryProcessor(query):
    with open("/Users/Zion/Downloads/AP_DATA/stoplist.txt") as sfile:
        stopWords = sfile.readlines()
    stopWords = filter(None, stopWords)
    keywords = ""
    flag = 0
    for word in query.split():
        for sWord in stopWords:
            if (word == sWord.strip()):
                flag = 1
                break
        if (flag != 1):
            keywords += word + " "
        flag = 0
    keywords = keywords.translate(None, string.punctuation)
    return keywords.strip()

def getInfo(key, catalog, termMap, docMap):
    keyInfo = OrderedDict()
    invList = OrderedDict()
    docDict = OrderedDict()
    indexFile = open("Files/Unstemmed/invertedFile0.txt", 'r')
    keyId = str(termMap.get(key))
    offset = catalog[keyId][0]
    indexFile.seek(int(offset))
    line = indexFile.readline()
    df = line.split(':')[0].split(',')[1]
    ttf = line.split(':')[0].split(',')[2]
    keyInfo[key] = [df, ttf]
    remStr = line.split(':')[1].split(';')
    for item in remStr:
        docno = item.split(',')[0]
        docID = docMap.get(int(docno))
        tf = int(item.split(',')[1])
        pos = [int(e) for e in item.split(',')[2:len(item.split(','))]]
        docDict[docID] = TermVector(tf, pos)
    invList[key] = docDict
    indexFile.close()
    return invList, keyInfo

def getParameters(query, qNo):
    keywords = queryProcessor(query)
    termVector = OrderedDict()
    termStats = OrderedDict()
    for key in keywords.split():

        key = key.lower()
        invList, keyInfo= getInfo(key, catalog, termMap, docMap)
        termVector.update(invList)
        termStats.update(keyInfo)
    f = open('Files/Unstemmed/Pickles/termStats_Proximity%s.p' % qNo, 'wb')
    dill.dump(termStats, f)
    f.close()
    f = open('Files/Unstemmed/Pickles/termVector_Proximity%s.p' % qNo, 'wb')
    dill.dump(termVector, f)
    f.close()

start_time = time.time()
docInfo = unpickler('Files/Unstemmed/Pickles/docInfo.p')
catalog = parseCatalog('Files/Unstemmed/catalogFile.txt')
termMap = unpickler('Files/Unstemmed/Pickles/termMap.p')
docMap = unpickler('Files/Unstemmed/Pickles/docMap.p')
# getInfo('govern', catalog, termMap, docMap)
queries = queryMaker()
qNo = 0
for query in queries:
    qNo += 1
    #if(qNo == 7):
    getParameters(query, qNo)

    print("Created %d termVector" % qNo)

temp = time.time() - start_time
print(temp)
hours = temp // 3600
temp = temp - 3600 * hours
minutes = temp // 60
seconds = temp - 60 * minutes
print('%d:%d:%d' % (hours, minutes, seconds))
