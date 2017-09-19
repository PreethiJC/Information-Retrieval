from elasticsearch_dsl import query, Search
from elasticsearch import Elasticsearch
import csv
import os
from string import digits
import string
from enchant.tokenize import get_tokenizer
import numpy
import enchant
from bs4 import BeautifulSoup
import dill
import time
import pandas
import numpy as np
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.decomposition import LatentDirichletAllocation
from sklearn.feature_extraction.text import TfidfTransformer
import pandas
from sklearn import linear_model
from sklearn import model_selection
from sklearn.preprocessing import Imputer
from sklearn.metrics import accuracy_score
from sklearn import preprocessing
from operator import itemgetter
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.naive_bayes import GaussianNB
import csv
from collections import OrderedDict

import os
import nltk
# nltk.download("words")
words = set(nltk.corpus.words.words())
# textList = []
# labelList = []
# docIDList = []
d = enchant.Dict("en_US")
def getText(path):
    for filename in os.listdir(path):
        if (filename != '.DS_Store'):
            print(filename)
            file = open(path + filename, "r", encoding="ISO-8859-1")
            page = file.read()
            validPage = "<root>" + page + "</root>"
            soup = BeautifulSoup(validPage, 'html.parser')
            label = soup.label.get_text()
            docID = soup.emailid.get_text()
            # if label == 'spam':
            texts = soup.find_all('text')
            text = ""
            for txt in texts:
                text += txt.get_text().strip()
            english_text = " ".join(w for w in nltk.wordpunct_tokenize(text) \
                     if w.lower() in words or not w.isalpha())
            textList.append(english_text)
            labelList.append(label)
            docIDList.append(docID)
            file.close()

def main():
    stoplist = open('/Users/Zion/Downloads/AP_DATA/stoplist.txt')
    stopwords = []

    for word in stoplist.readlines():
        stopwords.append(word.replace('\n', ''))
    stoplist.close()
    # getText('Files/')
    # print(labelList)
    # print(docIDList)
    # f = open("textListSpam.p", "wb")
    # dill.dump(textList, f)
    # f.close()
    # f = open("LabelList.p", "wb")
    # dill.dump(labelList, f)
    # f.close()
    # f = open("docIDList.p", "wb")
    # dill.dump(docIDList, f)
    # f.close()
    f = open("textListSpam.p", "rb")
    textList = dill.load(f)
    f.close()
    f = open("LabelList.p", "rb")
    LabelList = dill.load(f)
    f.close()
    f = open("docIDList.p", "rb")
    docIDList = dill.load(f)
    f.close()
    Y = numpy.array(LabelList)
    dID = numpy.array(docIDList)
    vectorizer = CountVectorizer(stop_words=stopwords)
    sparseMatrix = vectorizer.fit_transform(textList)
    kfold = model_selection.KFold(n_splits=5, random_state=None, shuffle=False)
    train, test = next(kfold.split(sparseMatrix, Y))
    docIDTest = dID[test]
    le = preprocessing.LabelEncoder()
    for i in range(0, len(LabelList)):
        Y = le.fit_transform(Y)
    print(Y)
    regr = linear_model.LogisticRegression()  # linear_model.LinearRegression()
    regr.fit(sparseMatrix[train], Y[train])  # train
    predictions = regr.predict(sparseMatrix[test])
    print(accuracy_score(Y[test], predictions.round()) * 100)
    # tf_transformer = TfidfTransformer(use_idf=False).fit(sparseMatrix)
    # X_train_tf = tf_transformer.transform(sparseMatrix)
    # print(len(vectorizer.get_feature_names()))
    # for feature in vectorizer.get_feature_names():
    #     print(feature)

main()