from __future__ import division
import math
from operator import itemgetter
from collections import defaultdict
import string
import dill

def restructureTV(termVector):
    dictDocID = defaultdict(lambda: defaultdict(list))
    for key in termVector:
        for docid in termVector[key]:
            dictDocID[docid][key] = [termVector[key][docid].getTF(), termVector[key][docid].getPos()]
    return dictDocID

def Total_okapiTF(qNo, termVector, termStats, docInfo):
    docScore = []
    dictDocID = restructureTV(termVector)

    for docid in dictDocID:
        tf = 0
        for key in dictDocID[docid]:
            tfwd = dictDocID[docid][key][0]
            docLen = int(docInfo.get(docid))
            tf += (tfwd / (tfwd + 0.5 + (1.5 * (docLen / avgDocLen))))
        docScore.append([docid, tf])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('Files/Unstemmed/OkapiTF_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def Okapi_BM25(qNo, termVector, termStats, docInfo):
    k1 = 1.2
    k2 = 1.2
    b = 0.75
    docScore = []
    dictDocID = restructureTV(termVector)
    for docid in dictDocID:
        bm25 = 0
        for key in dictDocID[docid]:
            tfwd = dictDocID[docid][key][0]
            docLen = int(docInfo.get(docid))
            df = int(termStats[key][0])
            op1 = (math.log10((D+0.5)/(df+0.5)))
            op2 = ((tfwd + (k1*tfwd))/(tfwd+(k1*((1-b)+(b*(docLen/avgDocLen))))))
            op3 = ((tfwd + (k2 * tfwd))/(tfwd + k2))
            bm25 += op1 * op2 * op3
        docScore.append([docid, bm25])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('Files/Unstemmed/OkapiBM25_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def UnigramLM_Laplace(qNo, catalog, termMap, docMap):
    keys = set()
    dictDocID = restructureTV(termVector)
    for doc_id in dictDocID:
        for key in dictDocID[doc_id]:
            keys.add(key)
    keys = list(keys)

    docScoreDict = {}
    for word in keys:
        for docid in dictDocID:
            dict = dictDocID[docid]
            if word in dict:
                tfwd = dict[word][0]
                docLen = int(docInfo.get(docid))
                score = float(tfwd + 1) / float(docLen + V)
            else:
                docLen = int(docInfo.get(docid))
                score = float(1) / float(docLen + V)
            if docid not in docScoreDict:
                docScoreDict[docid] = 0.0
            docScoreDict[docid] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)

    with open('Files/Unstemmed/UnigramLMLaplace_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %f Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def UnigramLM_JelinekMercer(qNo, termVector, termStats, docInfo):
    keys = set()
    dictDocID = restructureTV(termVector)
    for doc_id in dictDocID:
        for key in dictDocID[doc_id]:
            keys.add(key)
    keys = list(keys)
    l = 0.8
    docScoreDict = {}
    for word in keys:
        cTF = int(termStats[word][1])
        for docid in dictDocID:
            dict = dictDocID[docid]
            if word in dict:
                tfwd = dict[word][0]
                docLen = int(docInfo.get(docid))
                pML = cTF/V
                score = float(l * float(tfwd / docLen)) + (float(1 - l) * pML)
            else:
                docLen = int(docInfo.get(docid))
                pML = cTF/V
                score = (float(1 - l) * pML)
            if docid not in docScoreDict:
                docScoreDict[docid] = 0.0
            docScoreDict[docid] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)
    with open('Files/Unstemmed/UnigramLMJM_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def rangeOfWindow(pos):
    minROW = float("inf")
    keyPos = {}
    for key in pos:
        keyPos[key] = pos[key][0]
    maxLen = len(keyPos)
    while (maxLen == len(keyPos)):
        row = keyPos.get(max(keyPos, key=keyPos.get)) - keyPos.get(min(keyPos, key=keyPos.get))
        minKey = min(keyPos, key=keyPos.get)
        minPos = pos[minKey].index(keyPos.get(min(keyPos, key=keyPos.get)))
        if (minPos < (len(pos[minKey]) - 1)):
            newPos = pos[minKey][minPos + 1]
            keyPos[minKey] = newPos
        else:
            keyPos.pop(minKey)
        if row < minROW:
            minROW = row
    return minROW


def proximity(qNo, termVector, termStats, docInfo):
    docScore = []
    dictDocID = restructureTV(termVector)
    pos = {}
    c = 1500
    for docid in dictDocID:
        i = 0
        docLen = int(docInfo.get(docid))
        for key in dictDocID[docid]:
            pos[key] = dictDocID[docid][key][1]
            i+=1
        row = rangeOfWindow(pos)
        score = (c - row) * i / (docLen + V)
        docScore.append([docid, score])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('Files/Unstemmed/Results/Proximity_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def queryNums():
    f = open('QueryUpdated.txt', 'r')
    queries = []
    for line in f:
        queries.append(line.split()[0].translate(None, string.punctuation))
    return queries


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

termMap = unpickler('Files/Unstemmed/Pickles/termMap.p')
catalog = parseCatalog('Files/Unstemmed/catalogFile.txt')
docInfo = unpickler('Files/Unstemmed/Pickles/docInfo.p')
avgDocLen = sum(docInfo.values()) / len(docInfo)
#print avgDocLen  # res.aggregations.avg_size.value
V = len(catalog.keys())
#print(V)

D = 84678
qNums = queryNums()
i = 0
for qNo in qNums:
    i += 1
    termStats = unpickler('Files/Unstemmed/Pickles/termStats_Proximity%s.p' % i)
    termVector = unpickler('Files/Unstemmed/Pickles/termVector_Proximity%s.p' % i)
    print("Running Query %d out of 25" % i)
    # Total_okapiTF(qNo, termVector, termStats, docInfo)
    # Okapi_BM25(qNo, termVector, termStats, docInfo)
    # UnigramLM_Laplace(qNo, termVector, termStats, docInfo)
    proximity(qNo, termVector, termStats, docInfo)
    # UnigramLM_JelinekMercer(qNo, termVector, termStats, docInfo)
print("Done!")