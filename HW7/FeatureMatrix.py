from elasticsearch_dsl import query, Search
from elasticsearch import Elasticsearch
import csv
import os
from string import digits
import string
from enchant.tokenize import get_tokenizer
import enchant
from bs4 import BeautifulSoup
import dill
import time
from nltk.corpus import stopwords
import nltk

es = Elasticsearch()
featureMatrix = {}
uniGrams = set()

def getText(path):
    prevDoc = []
    for filename in os.listdir(path):
        if (filename != '.DS_Store'):
            print(filename)
            file = open(path + filename, "r", encoding="ISO-8859-1")
            page = file.read()
            validPage = "<root>" + page + "</root>"
            soup = BeautifulSoup(validPage, 'html.parser')
            texts = soup.find_all('text')
            text = ""
            for txt in texts:
                text += txt.get_text().strip()
            if(len(uniGrams) < 200):
                getTokens(text)
            else:
                break
            # print(len(uniGrams))

def getTokens(text):
    tknzr = get_tokenizer("en_US")
    words = [w[0].lower() for w in tknzr(text)]
    getUnigrams(words)

def getUnigrams(wrdList):
    d = enchant.Dict("en_US")
    for w in wrdList:
        if d.check(w):
            uniGrams.add(w)


def getAllDocIds():
    s = Search().using(es).index('hw7_index').query("match_all")
    docIDLabel = [(h.meta.id, h.label) for h in s.scan()]
    return docIDLabel

def getDocScore(term):
    s = Search().using(es).index('hw7_index').query("multi_match", query=term, fields=["text"])
    s = s.extra(track_scores=True)
    docInfo = [(h.meta.id, h.meta.score) for h in s.scan()]
    return docInfo

def populateFeatureMatrix(nGramList):
    colNames = []
    i = len(nGramList)
    for nGram in nGramList:
        print("%d left out of %d" %(i, len(nGramList)))
        i -= 1
        nGram = nGram.strip()
        colNames.append(nGram)
        docInfo = getDocScore(nGram)
        for docScorePair in docInfo:
            featureMatrix[docScorePair[0]][nGram] = docScorePair[1]
    return colNames

def getNGrams(file):
    with open(file, "r") as nGramFile:
        colNames = populateFeatureMatrix(nGramFile.readlines())
    nGramFile.close()
    return colNames


def createSparseMatrix(nGrams, filename, docIDLabel):
    nGramLen = len(nGrams)
    colNames = []
    colNames += nGrams
    colNames.append('Label')
    colNames.insert(0, 'DocID')
    with open(filename+'.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter=',', quoting=csv.QUOTE_NONE)
        filewriter.writerow(colNames)
        i = 0
        for key, value in featureMatrix.items():
            i += 1
            print("%dth row created for DocID %s" %(i,key))
            scores = [""] * nGramLen
            row = []
            for vvKey, vvValue in value.items():
                    if vvKey in nGrams:
                        scores[nGrams.index(vvKey)] = vvValue
            row.append(key)
            row += scores
            row.append([item for item in docIDLabel if item[0] == key][0][1])


                    # for id in featureMatrix:
        #     i+=1
        #     print("%dth row created for DocID %s" %(i,id))
        #     scores = [""] * nGramLen
        #     row = []
        #     for label in featureMatrix[id]:
        #         for wrd in featureMatrix[id][label]:
        #             score = featureMatrix[id][label][wrd]
        #             for colName in nGrams:
        #                 if colName == wrd:
        #                     scores[nGrams.index(colName)] = score
        #         row.append(id)
        #         row += scores
        #         row.append(label)
            filewriter.writerow(row)
    csvfile.close()

def removeStopWords(nGrams):
    with open("/Users/Zion/Downloads/AP_DATA/stoplist.txt") as sfile:
        stopWords = sfile.readlines()
    stopWords = list(filter(None, stopWords))
    keywords = list()
    flag = 0
    i = len(nGrams)
    for word in nGrams:
        # print("%d terms remaining out of %d" % (i, len(nGrams)))
        i -= 1
        for sWord in stopWords:
            if (word.lower() == sWord.strip()):
                flag = 1
                break
            elif len(word) < 2:
                flag = 1
                break
        if (flag != 1):
            keywords.append(word.lower())
        flag = 0
    with open("scratch.txt", "w") as s:
        for k in keywords:
            s.write(k + "\n")
    s.close()
    return keywords

def generateNGrams(path):
    getText(path)
    f = open("Unigrams200.p", "wb")
    dill.dump(uniGrams, f)
    f.close()

def fullFledged(path, docIDLabel):
    generateNGrams(path)
    # f = open('Unigrams.p', 'rb')
    # uni = dill.load(f)
    # f.close()
    nGrams = list(uniGrams)
    cleanNGrams = removeStopWords(nGrams)
    # f = open('FeatureMatrix200.p', 'rb')
    # NGrams = dill.load(f)
    # f.close()
    # cleanNGrams = removeStopWords(NGrams)
    NGrams = populateFeatureMatrix(cleanNGrams)
    f = open("FeatureMatrix200.p", "wb")
    dill.dump(featureMatrix, f)
    f.close()
    createSparseMatrix(NGrams, "staticFeatureMatrixFull200", docIDLabel)

def main():
    docIDLabel = getAllDocIds()
    for idLabel in docIDLabel:
        featureMatrix[idLabel[0]] = {}
    # nGrams = getNGrams('manual.txt')
    # createSparseMatrix(nGrams, "staticFeatureMatrixManual")
    # nGrams = getNGrams('spam_words.txt')
    # createSparseMatrix(nGrams, "staticFeatureMatrixGiven2", docIDLabel)

    fullFledged("Files/", docIDLabel)


start_time = time.time()
main()
temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))