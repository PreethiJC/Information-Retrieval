from collections import OrderedDict
import re
import math
from string import digits
import string
import dill
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search
import csv


relevanceJudgements = {}
featureMatrix = OrderedDict()
qrelDocIDs = []
es = Elasticsearch()

s = Search().using(es).query("match_all")
s.aggs.bucket("avg_size", "avg", field="doc_len")
s.aggs.bucket("vocabSize", "cardinality", field="text")
res = s.execute()
V = res.aggregations.vocabSize.value
cTF = []
bm25Scores = {}
jmScores = {}
lScores = {}
oTFScores = {}
tfIDFScores = {}
bm25Scores1000 = {}
jmScores1000 = {}
lScores1000 = {}
oTFScores1000 = {}
tfIDFScores1000 = {}
docIDLst = {}
f = open('totalTF.p', 'rb')
cTF = dill.load(f)
f.close()

relevance = {}
def getRevelanceJudgements(qrel):
    with open(qrel, 'r') as f:
        for judgement in f:
            cols = judgement.split(' ')
            queryID = cols[0]
            documentID = cols[2]
            if queryID in relevance:
                relevance[queryID][documentID] = int(cols[3])
            else:
                relevance[queryID] = {}
                relevance[queryID][documentID] = int(cols[3])
            qrelDocIDs.append(documentID)
            if queryID in relevanceJudgements:
                relevanceJudgements[queryID].append((documentID, 'na'))
            else:
                relevanceJudgements[queryID] = [(documentID, 'na')]
    f.close()

def getDocScoreFromRM(rmFile, ds):
    with open(rmFile, 'r') as f:
        for res in f:
            cols = res.split(' ')
            queryID = cols[0]
            documentID = cols[2]
            score = cols[4].strip()
            qrelDocIDs.append(documentID)
            if queryID in ds:
                ds[queryID].append((documentID, score))
            else:
                ds[queryID] = [(documentID, score)]
    f.close()

def queryProcessor(query):
    with open("/Users/Zion/Downloads/AP_DATA/stoplist.txt") as sfile:
        stopWords = sfile.readlines()
    stopWords = list(filter(None, stopWords))
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
    table = str.maketrans(dict.fromkeys(string.punctuation))
    keywords = keywords.translate(table)
    return keywords.strip()

def queryMaker(qID):
    f = open('QueryUpdated.txt', 'r')
    queries = []
    for line in f:
        qNo = line.split('.', 1)[0]
        if(qNo == str(qID)):
            table = str.maketrans(dict.fromkeys(digits))
            queries.append(re.sub('\s+', ' ', line).strip().translate(table))
    return queries

def UnigramLM_Laplace(qNo, docID, query):
    keywords = queryProcessor(query).lower()
    docScore = 0.0
    keys = []
    for item in cTF:
        if (item[1] in keywords.split()):
            keys.append(item[1])
    for key in keys:
        docLen = len(es.termvectors(index="index1", doc_type="document", id=docID, term_statistics=True)["term_vectors"] \
        ["text"]["terms"].keys())
        score = float(1) / float(docLen + V)
        docScore += math.log(score)
    return docScore

def UnigramLM_JelinekMercer(qNo, query):
    keywords = queryProcessor(query).lower()
    l = 0.8
    docScore = 0.0
    keys = []
    for item in cTF:
        if(item[1] in keywords.split()):
            keys.append(item[1])
    for key in keys:
        pML = list((filter(lambda x: x[1] == key.lower(), cTF)))[0][0]/ V
        score = (float(1 - l) * pML)
        docScore += math.log(score)
    return docScore

def get1000Scores(ds, opt=0):
    ds1000 = {}

    for qID in relevanceJudgements:
        if qID in ds:
            ds1000[qID] = []
            if (opt != 0):
                docIDLst[qID] = []
            for docScorePair in relevanceJudgements[qID]:
                if(opt != 0):
                    docIDLst[qID].append(docScorePair[0])
                    pair = [item for item in ds[qID] if item[0] == docScorePair[0]]
                    if pair:
                        score = pair[0][1]
                    else:
                        score = ''
                    ds1000[qID].append((docScorePair[0], score))
                else:
                    if(docScorePair[0] in docIDLst[qID]):
                        pair = [item for item in ds[qID] if item[0] == docScorePair[0]]
                        if pair:
                            score = pair[0][1]
                        else:
                            score = ''
                        ds1000[qID].append((docScorePair[0], score))
            if len(ds1000[qID]) < 1000:
                ds[qID].reverse()
                limit = len(ds1000[qID])
                for docScorePair in ds[qID]:
                    if(limit < 1000):
                        pair = [item for item in ds1000[qID] if item[0] == docScorePair[0]]
                        if pair:
                            continue
                        else:
                            if (opt != 0):
                                docIDLst[qID].append(docScorePair[0])
                                ds1000[qID].append(docScorePair)
                                limit += 1
                            else:
                                if (docScorePair[0] in docIDLst[qID]):
                                    ds1000[qID].append(docScorePair)
                                    limit += 1
                    else:
                        break
            print(len(docIDLst[qID]))
    return ds1000

def generateScores(ds1000, model):
    ds1000Temp = {}
    for qid in ds1000:
        flag = 0
        ds1000Temp[qid] = []
        for docScorePair in ds1000[qid]:
            pair = [item for item in ds1000[qid] if item[0] == docScorePair[0]][0][1]
            if pair == '':
                flag = 1
                query = queryMaker(qid)
                if model == 'BM25' or model == 'TF-IDF' or model=='Okapi TF':
                    pair = 0
                elif model == 'Jelinek-Mercer':
                    pair = UnigramLM_JelinekMercer(qid, query[0])
                else:
                    pair = UnigramLM_Laplace(qid, docScorePair[0], query[0])
            ds1000Temp[qid].append((docScorePair[0], pair))
    return ds1000Temp
        # print(len(ds1000[qid]))

def validateDS(ds1000):
    for qid in ds1000:
# print(len(ds1000[qid]))
        i = 0
        for docScorePair in ds1000[qid]:
            i += 1
            if docScorePair[0] not in docIDLst[qid]:
                print('Mismatch! ', str(qid), docScorePair[0])
    # with open('ModelMatrix.csv', 'a') as csvfile:
    #     filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
    #     filewriter.writerow(['QID', 'DocID', 'Score', 'i'])
    #     for qid in ds1000:
    #         # print(len(ds1000[qid]))
    #         i = 0
    #         for docScorePair in ds1000[qid]:
    #             i += 1
    #             filewriter.writerow([qid, docScorePair[0], docScorePair[1], i])
    #         # pair = [item for item in ds1000[qid] if item[0] == docScorePair[0]][0][1]
    #         # if pair == '':
    #         #     print(qid, docScorePair[0])
    # csvfile.close()

def createFeatureMatrix(ds1000, model, opt=0):
    idLst = []
    for qID in ds1000:
        for docScorePair in ds1000[qID]:
            if docScorePair[0] in relevance[qID]:
                label = relevance[qID][docScorePair[0]]
            else:
                label = 0

            identifier = str(qID) + '-' + docScorePair[0]
            idLst.append(identifier)
            if opt != 0:
                featureMatrix[identifier] = OrderedDict()
                featureMatrix[identifier][model] = [docScorePair[1], label]
            else:
                featureMatrix[identifier][model] = [docScorePair[1], label]

def staticFeatureMatrixCSV():
    row = ""
    tfIDF = ""
    bm25 = ""
    oTF = ""
    jm = ""
    l = ""
    label = ""
    with open('staticFeatureMatrix.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
        filewriter.writerow(['QID-DocID', 'TF-IDF', 'Okapi TF', 'BM25', 'Laplace', 'Jelinek-Mercer', 'Label'])
        for identifier in featureMatrix:
            for model in featureMatrix[identifier]:
                score = featureMatrix[identifier][model][0]
                label = featureMatrix[identifier][model][1]
                if model == 'BM25':
                    bm25 = score
                elif model == 'TF-IDF':
                    tfIDF = score
                elif model == 'Okapi TF':
                    oTF = score
                elif model == 'Jelinek-Mercer':
                    jm = score
                elif model == 'Laplace':
                    l = score
            filewriter.writerow([identifier, tfIDF, oTF, bm25, l, jm, label])
    csvfile.close()

def main():
    getRevelanceJudgements("qrels.adhoc.51-100.AP89.txt")

    getDocScoreFromRM("OkapiBM25_Results_File.txt", bm25Scores)
    getDocScoreFromRM("UnigramLMJM_Results_File.txt", jmScores)
    getDocScoreFromRM("UnigramLMLaplace_Results_File.txt", lScores)
    getDocScoreFromRM("OkapiTF_Results_File.txt", oTFScores)
    getDocScoreFromRM("TF-IDF_Results_File.txt", tfIDFScores)

    bm25Scores1000 = get1000Scores(bm25Scores, 1)
    jmScores1000 = get1000Scores(jmScores)
    lScores1000 = get1000Scores(lScores)
    oTFScores1000 = get1000Scores(oTFScores)
    tfIDFScores1000 = get1000Scores(tfIDFScores)

    bm25Scores1000Scored = generateScores(bm25Scores1000, 'BM25')
    jmScores1000Scored = generateScores(jmScores1000, 'Jelinek-Mercer')
    lScores1000Scored = generateScores(lScores1000, 'Laplace')
    oTFScores1000Scored = generateScores(oTFScores1000, 'Okapi TF')
    tfIDFScores1000Scored = generateScores(tfIDFScores1000, 'TF-IDF')
    # print(len(bm25Scores1000))
    validateDS(bm25Scores1000Scored)
    validateDS(jmScores1000Scored)
    validateDS(lScores1000Scored)
    validateDS(oTFScores1000Scored)
    validateDS(tfIDFScores1000Scored)
    #

    createFeatureMatrix(tfIDFScores1000Scored, 'TF-IDF', 1)
    createFeatureMatrix(oTFScores1000Scored, 'Okapi TF')
    createFeatureMatrix(bm25Scores1000Scored, 'BM25')
    createFeatureMatrix(lScores1000Scored, 'Laplace')
    createFeatureMatrix(jmScores1000Scored, 'Jelinek-Mercer')
    #
    #
    staticFeatureMatrixCSV()

main()




