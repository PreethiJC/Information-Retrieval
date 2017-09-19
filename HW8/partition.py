from bs4 import BeautifulSoup
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.cluster import KMeans
import os

docMap = {}
docText = []
relDoc = {}
T = 200
W = 30
C = 25
VectorMatrix = None
clusters = {}

def buildDocText():
    path = "AP_DATA/ap89_collection/"
    i = 0
    for filename in os.listdir(path):
        if(filename != 'readme'):
            file = open(path+filename, encoding='utf-8', errors='replace')
            page = file.read()
            validPage = "<root>" + page + "</root>"
            soup = BeautifulSoup(validPage, 'xml')
            docs = soup.find_all('DOC')
            for doc in docs:
                docMap[i] = doc.find('DOCNO').get_text().strip()
                i+=1
                texts = doc.find_all('TEXT')
                text = ""
                for txt in texts:
                    text += txt.get_text()
                #if i > 10000: Uncomment this to run for 10000 docs
                    #return

                docText.append(text)

def printTopics2(model, feature_names):
    text = ''
    for topic_id, topic in enumerate(model.components_):
        line = '\nTopic %d: ' % (int(topic_id + 1))
        line += printTopicTopWords(topic, feature_names)
        text += line
        
    return text
                
def printTopics(docRow, model, feature_names):
    text = ''
    for topic_id in range(0, len(docRow)):
        line = '\nTopic %d: (%f)' % (int(topic_id + 1), round(docRow[topic_id], 10))
        #line += printTopicTopWords(topic, feature_names)
        text += line
        
    return text

def printDocs(docs_topic_distribution, model, feature_names):
    print("Total Distributions: %d" % len(docs_topic_distribution))
    folder = 'partB_clusters/'
    for n in range(docs_topic_distribution.shape[0]):
        text = "topics: {}\n {}".format(docMap[n], printTopics(docs_topic_distribution[n], model, feature_names))
        f = open(folder + docMap[n] + '.txt', "w")
        f.write(text)
        f.close()
        if n % 1000 == 0:
            print("Finished %d" % n)

def printTopicTopWords(topic, feature_names):
    return ''.join([feature_names[i] + ' ' + str(round(topic[i], 2))
                         +' | ' for i in topic.argsort()[:-W - 1:-1]])

def runLDA():
    print ("LDA")
    global VectorMatrix, docText
    stoplist = open('AP_DATA/stoplist.txt')
    stopwords = []
    for word in stoplist.readlines():
        stopwords.append(word.replace('\n',''))
    stoplist.close()

    vectorizer = CountVectorizer(stop_words = stopwords, max_features = 10000)
    sparseMatrix = vectorizer.fit_transform(docText)
    lda = LatentDirichletAllocation(n_components = T, max_iter=5,
                                    learning_method='online',
                                    learning_offset=50., random_state=0)
    lda.fit(sparseMatrix)
    featureNames = vectorizer.get_feature_names()
    VectorMatrix = lda.transform(sparseMatrix)
    
    f= open('partB_clusterTopics/topics.txt', 'w')
    f.write(printTopics2(lda, featureNames))
    f.close()
    docText = None
    # printDocs(lda.transform(sparseMatrix), lda, featureNames)
    

def printClusters():
    global clusters
    f = open('partB_clusterTopics/clusters.txt', 'w')
    for label in clusters:
        line = 'Cluster %d: ' % label
        line += ','.join(clusters[label])
        line += '\n'
        f.write(line)

    f.close()

def runKmeans():
    print("K Means")
    global clusters
    kMeans = KMeans(n_clusters = W)
    kMeans.fit(VectorMatrix)
    for labelIndex in range(0, len(kMeans.labels_)):
        if kMeans.labels_[labelIndex] not in clusters:
            clusters[kMeans.labels_[labelIndex]] = set()
        clusters[kMeans.labels_[labelIndex]].add(docMap[labelIndex])
    
    printClusters()

def buildRelevantDocs():
    global relDoc, mapDoc
    f = open('qrels.adhoc.51-100.AP89.txt', "r")
    for line in f.readlines():
        words = line.split(' ')
        if words[3][:-1] == '1':
            if words[2] not in relDoc:
                relDoc [words[2]]= set()
            relDoc[words[2]].add(words[0])

    f.close()

def combinations_of_2(l):
    for i, j in zip(*np.triu_indices(len(l), 1)):
        yield l[i], l[j]

def isSQ(doc1, doc2):
    for query in relDoc[doc1]:
        if query in relDoc[doc2]:
            return True
    return False

def isSC(doc1, doc2):
    for cluster in clusters:
        if doc1 in clusters[cluster] and doc2 in clusters[cluster]:
            return True
    return False

def isFetched(doc1, doc2):
    return True # Comment this and Uncomment below to run for 10000
    '''
    flag1 = False
    flag2 = False
    for cluster in clusters:
        if doc1 in clusters[cluster]:
            flag1 = True
        if doc2 in clusters[cluster]:
            flag2 = True
    return (flag1 and flag2)
    '''

def evaluate():
    print("Evaluating")
    global comb
    SQSC = 0
    SQDC = 0
    DQSC = 0
    DQDC = 0
    for comb in combList:
        doc1 = comb[0]
        doc2 = comb[1]
        if isFetched(doc1, doc2):
            if isSQ(doc1, doc2) and isSC(doc1, doc2):
                SQSC += 1
            elif isSQ(doc1, doc2) and (not isSC(doc1, doc2)):
                SQDC += 1
            elif (not isSQ(doc1, doc2)) and isSC(doc1, doc2):
                DQSC += 1
            else:
                DQDC += 1

    accuracy = float((SQSC + DQDC))/(SQSC + DQDC + DQSC + SQDC)
    return accuracy

buildDocText()
print("Total docs files: %d" % len(docMap)) 
runLDA()
runKmeans()
buildRelevantDocs()
combList = list(combinations_of_2(list(relDoc.keys())))
print(evaluate())

