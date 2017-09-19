from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
import os

topBM25 = {}
topQREL = {}

topicThreshold = 30
topWords = 30

def buildDict(file):
    topDict = {}
    for line in file.readlines():
        words = line.split(' ')
        if words[0] not in topDict:
            topDict[words[0]] = set()
        if len(topDict[words[0]]) < 1000:
            topDict[words[0]].add(words[2])

    return topDict
                

def buildTopDocs(resultFile, model):
    global topBM25, topQREL
    f = open(resultFile)
    if model == 'BM25':
        topBM25 = buildDict(f)
    elif 'QREL':
        topQREL = buildDict(f)
    f.close()


def queryDocUnion(queryId):
    return topBM25[queryId].union(topQREL[queryId])


def getDocText(docFile, docId):
    path = "AP_DATA/ap89_collection/"
    file = open(path+docFile, encoding='utf-8', errors='replace')
    page = file.read()
    validPage = "<root>" + page + "</root>"
    soup = BeautifulSoup(validPage, 'xml')
    docs = soup.find_all('DOC')
    for doc in docs:
        if (doc.find('DOCNO').get_text().strip()) == docId:
            texts = doc.find_all('TEXT')
            print (len(texts))
            input()
            text = ""
            for txt in texts:
                text += txt.get_text()
            file.close()
            return text

    return ''
    
def printTopics(model, feature_names, n_top_words, topTopics = {}):
    text = ''
    for topic_id, topic in enumerate(model.components_):
        if len (topTopics) > 0:
            if topic_id not in topTopics:
                continue
            line = '\nTopic %d (%f):' % (int(topic_id + 1), topTopics[topic_id])
        else:
            line = '\nTopic %d:' % (int(topic_id + 1))
        line += printTopicTopWords(topic, feature_names, n_top_words)
        text += line
    return text

def getTop10Topics(doc_topic):
    topic_most_pr = doc_topic.argsort()[:-10-1:-1]
    top = {}
    for i in topic_most_pr:
        top[i] = round(doc_topic[i], 5)

    return top

def printDocs(docs_topic_distribution, feature_names, docMap, model, n_top_words):
    text = ''
    for n in range(docs_topic_distribution.shape[0]):
        topic_most_pr = getTop10Topics(docs_topic_distribution[n])
        text += "\ndoc {} top 10 topics: {}\n".format(docMap[n],
                                            printTopics(model, feature_names, n_top_words, topic_most_pr))

    return text

def printTopicTopWords(topic, feature_names, n_top_words):
    return ''.join([feature_names[i] + ' ' + str(round(topic[i], 2))
                         +' | ' for i in topic.argsort()[:-n_top_words - 1:-1]])
        
def runLDA():
    stoplist = open('AP_DATA/stoplist.txt')
    stopwords = []
    for word in stoplist.readlines():
        stopwords.append(word.replace('\n',''))
    stoplist.close()

    tot = 1
    for queryId in topBM25:
        if tot == 25:
            break
        if queryId in topQREL:
            print (queryId)
            queryDocs = queryDocUnion(queryId)
            textDocs = []
            docMap = {}
            i = 0
            for docId in queryDocs:
                textDocs.append(getDocText(docId.split('-')[0], docId))
                docMap[i] = docId
                i+=1
                
            vectorizer = CountVectorizer(stop_words = stopwords)
            sparseMatrix = vectorizer.fit_transform(textDocs)

            lda = LatentDirichletAllocation(n_components = topicThreshold, max_iter=5, 
                                        learning_method='online',                 
                                        learning_offset=50., random_state=0)

            lda.fit(sparseMatrix)

            f1 = open('partA_topics/query' + queryId + '.txt', "w")
            f1.write(printTopics(lda, vectorizer.get_feature_names(), topWords))
            f1.close()
            
            f2 = open('partA_docs/query' + queryId + '.txt', "w")
            f2.write(printDocs(lda.transform(sparseMatrix), vectorizer.get_feature_names(), docMap, lda, topWords))
            
            f2.close()
            
            tot += 1
    

buildTopDocs('qrels.adhoc.51-100.AP89.txt', 'QREL')
buildTopDocs('OkapiBM25_Results_File.txt', 'BM25')

runLDA()

        
    
