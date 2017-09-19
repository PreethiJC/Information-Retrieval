from __future__ import division
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import math
from operator import itemgetter
import string
import dill

es = Elasticsearch()


s = Search().using(es).query("match_all")
s.aggs.bucket("avg_size", "avg", field="doc_len")
s.aggs.bucket("vocabSize", "cardinality", field="text")
res = s.execute()
D = 84678
avgDocLen = 20969809/84660 #res.aggregations.avg_size.value
V = res.aggregations.vocabSize.value
print(V)

def Total_okapiTF(qNo, termVector):
    docScore = []
    for docid in termVector:
        tf = 0
        for key in termVector[docid]:
            tfwd = termVector[docid][key][0]
            docLen = termVector[docid][key][1]
            tftemp = (tfwd/(tfwd + 0.5 + (1.5 * (docLen/avgDocLen))))
            tf += (tfwd/(tfwd + 0.5 + (1.5 * (docLen/avgDocLen))))
        docScore.append([docid, tf])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('/Users/Zion/Desktop/Desktop - Zion/NEU/Sem 2/Information Retrieval/HW6/OkapiTF_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%d Q0 %s %d %lf Exp\n' % (int(qNo), ds[0], rank, ds[1]))
            # if rank == 1000:
            #         break
            rank += 1

def TF_IDF(qNo, termVector, docFreq):
    docScore = []
    for docid in termVector:
        tf = 0
        for key in termVector[docid]:
            tfwd = termVector[docid][key][0]
            docLen = termVector[docid][key][1]
            tf += ((tfwd / (tfwd + 0.5 + (1.5 * (docLen / avgDocLen)))) * (math.log10(D/list(filter(lambda x:x[0]==key, docFreq))[0][1])))
        docScore.append([docid, tf])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('/Users/Zion/Desktop/Desktop - Zion/NEU/Sem 2/Information Retrieval/HW6/TF-IDF_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            # if rank == 1000:
            #     break
            rank += 1

def Okapi_BM25(qNo, termVector, docFreq):
    k1 = 1.2
    k2 = 1.2
    b = 0.75
    docScore = []
    for docid in termVector:
        bm25 = 0
        for key in termVector[docid]:
            tfwd = termVector[docid][key][0]
            docLen = termVector[docid][key][1]
            df = list(filter(lambda x:x[0]==key, docFreq))[0][1]
            op1 = (math.log10((D+0.5)/(df+0.5)))
            op2 = ((tfwd + (k1*tfwd))/(tfwd+(k1*((1-b)+(b*(docLen/avgDocLen))))))
            op3 = ((tfwd + (k2 * tfwd))/(tfwd + k2))
            bm25 += op1 * op2 * op3
        docScore.append([docid, bm25])
    docScore.sort(key=itemgetter(1), reverse=True)
    with open('/Users/Zion/Desktop/Desktop - Zion/NEU/Sem 2/Information Retrieval/HW6/OkapiBM25_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in docScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            # if rank == 1000:
            #     break
            rank += 1

def UnigramLM_Laplace(qNo, termVector):
    keys = set()
    for doc_id in termVector:
        for key in termVector[doc_id]:
            keys.add(key)
    keys = list(keys)

    docScoreDict = {}
    for word in keys:
        for docid in termVector:
            dict = termVector[docid]
            if word in dict:
                tfwd = dict[word][0]
                docLen = dict[word][1]
                score = float(tfwd + 1) / float(docLen + V)
            else:
                docLen = dict[dict.keys()[0]][1]
                score = float(1) / float(docLen + V)
            if docid not in docScoreDict:
                docScoreDict[docid] = 0.0
            docScoreDict[docid] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)

    with open('/Users/Zion/Desktop/Desktop - Zion/NEU/Sem 2/Information Retrieval/HW6/UnigramLMLaplace_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %f Exp\n' % (qNo, ds[0], rank, ds[1]))
            # if rank == 1000:
            #     break
            rank += 1

def UnigramLM_JelinekMercer(qNo, termVector):
    keys = set()
    for doc_id in termVector:
        for key in termVector[doc_id]:
            keys.add(key)
    keys = list(keys)
    l = 0.8
    docScoreDict = {}
    for word in keys:
        for docid in termVector:
            dict = termVector[docid]
            if word in dict:
                tfwd = dict[word][0]
                docLen = dict[word][1]
                pML = (filter(lambda x: x[1] == word, cTF)[0][0]) / V
                score = float(l * float(tfwd / docLen)) + (float(1 - l) * pML)
            else:
                docLen = dict[dict.keys()[0]][1]
                pML = (filter(lambda x: x[1] == word, cTF)[0][0]) / V
                score = (float(1 - l) * pML)
            if docid not in docScoreDict:
                docScoreDict[docid] = 0.0
            docScoreDict[docid] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)
    with open('/Users/Zion/Desktop/Desktop - Zion/NEU/Sem 2/Information Retrieval/HW6/UnigramLMJM_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            # if rank == 1000:
            #     break
            rank += 1

def queryNums():
    f = open('Files/QueryUpdated.txt', 'r')
    queries = []
    for line in f:
        queries.append(line.split()[0].translate(None, string.punctuation))
    return queries

qNums = queryNums()
i = 0
f = open('Pickles/totalTF.p', 'rb')
cTF = dill.load(f)
f.close()
for qNo in qNums:
    i += 1
    # if i == 1:
    f = open('Pickles/docFreq%s.p' % i, 'rb')
    docFreq = dill.load(f)
    f.close()
    f = open('Pickles/termVector%s.p' % i, 'rb')
    termVector = dill.load(f)
    f.close()
    print("Running Query %d out of 25" % i)
    Total_okapiTF(qNo, termVector)
    TF_IDF(qNo, termVector, docFreq)
    Okapi_BM25(qNo, termVector, docFreq)
    UnigramLM_Laplace(qNo, termVector)
    UnigramLM_JelinekMercer(qNo, termVector)
print("Done!")