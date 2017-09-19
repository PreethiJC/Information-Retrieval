import numpy as np
from sklearn.model_selection import train_test_split
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


def createDict(dIDTest, probabilities, labels):
    probabilitiesList = list(probabilities)
    testDict = OrderedDict()
    i = 0
    sortedProbabilities = []
    sortedProbabilities += probabilitiesList
    sortedProbabilities.sort()
    for probability in enumerate(sortedProbabilities):
        i = probabilitiesList.index(sortedProbabilities[probability[0]])
        docID = dIDTest[i][0]
        label = labels[i]
        testDict[docID] = []
        testDict[docID].append((label, probability[1]))
    return testDict

def sortDict(testDict):
    for item in testDict:
        sorted_list = sorted(testDict[item], key=itemgetter(1))
        testDict[item] = sorted_list
    return testDict

def createPerformanceFile(testDict):
    with open( 'Ranking.csv', 'w') as csvfile:
        filewriter = csv.writer(csvfile, delimiter='|', quoting=csv.QUOTE_NONE)
        i = 0
        for item in testDict:
            for labelScorePair in testDict[item]:
                i+=1
                row = [item, labelScorePair[0], i, labelScorePair[1]]

                filewriter.writerow(row)
    # with open('Ranking.txt', 'w') as f:
    #     i = 0
    #     for item in testDict:
    #         i = 0
    #         for labelScorePair in testDict[item]:
    #             i+=1
    #             f.write("%s %s %d %f \n" %(item, labelScorePair[0], i, labelScorePair[1]))
    # f.close()
    csvfile.close()

def getNGrams(file):
    colNames = []
    with open(file, "r") as nGramFile:
        for nGram in nGramFile.readlines():
            nGram = nGram.strip()
            colNames.append(nGram)
    nGramFile.close()
    return colNames

def getBestFeatures(X, y, csvFile, names):
    dataset = pandas.read_csv(csvFile, names=names)
    # print(dataset.columns[0:len(names)])
    selector = SelectKBest(f_classif, k=10)
    selector.fit_transform(X, y)
    # print(len(X[0]))
    # print(len(selector.get_support()))
    names = dataset.columns[0:len(names)-1].values[selector.get_support()]
    scores = selector.scores_[selector.get_support()]
    names_scores = list(zip(names, scores))
    ns_df = pandas.DataFrame(data=names_scores, columns=['Feat_names', 'F_Scores'])
    # Sort the dataframe for better visualization
    ns_df_sorted = ns_df.sort_values(['F_Scores', 'Feat_names'], ascending=[False, True])
    print(ns_df_sorted)


def getAccuracy(txtFile, csvFile):
    docID = ['DocID']

    df = pandas.read_csv(csvFile, skipinitialspace=True,
                         usecols=docID)  # contains query ID and doc ID
    df_array = df.values
    dID = df_array
    names = getNGrams(txtFile)
    dataset = pandas.read_csv(csvFile, names=names, skiprows=[0])#contains retrieval model scores and label
    for name in names:
        if dataset[name].notnull().sum() == 0:
            dataset[name] = 0
            # print(name, dataset[name].notnull().sum())
    # fill_NaN = Imputer(missing_values=np.nan, strategy='mean', axis=1)
    # imputed_DF = pandas.DataFrame(fill_NaN.fit_transform(dataset))
    # imputed_DF.columns = dataset.columns
    # imputed_DF.index = dataset.index
    array = dataset.values
    # print(array)
    # print(array[:,0:19])
    lenNGrams = len(names) - 1

    X = array[:,0:lenNGrams] #contains only retrieval model scores
    Y = array[:,lenNGrams]
    print(X)
    # print(Y)

    le = preprocessing.LabelEncoder()
    for i in range(0, len(names)):
        Y = le.fit_transform(Y)
    print(Y)
    fill_NaN = Imputer()
    # fill_NaN = Imputer(missing_values=np.nan, strategy='mean', axis=1)
    imputed_DF = pandas.DataFrame(fill_NaN.fit_transform(X))
    # imputed_DF.columns = X.columns
    # imputed_DF.index = X.index
    array = imputed_DF.values
    X = array[:,0:lenNGrams]  # contains only retrieval model scores
    # Y = array[:,lenNGrams-2]
    # print(X)
    # imputer = Imputer()
    # transformed_X = imputer.fit_transform(X)
    # print(X[0])
    # print(transformed_X[0])

    kfold = model_selection.KFold(n_splits=5, random_state=None, shuffle=False)
    train, test = next(kfold.split(X, Y))
    docIDTest = dID[test]
    regr = linear_model.LogisticRegression()#linear_model.LinearRegression()
    regr.fit(X[train], Y[train])#train
    predictions = regr.predict(X[test])
    # probabilities = regr.predict_proba(X[test])[:,1]
    # print(probabilities)
    # testDict = createDict(docIDTest, probabilities, Y[test])
    # # testDict = sortDict(testDict)
    # createPerformanceFile(testDict)
    print(accuracy_score(Y[test], predictions.round()) *100)
    getBestFeatures(X, Y, csvFile, names)

def main():
    # getAccuracy('manual.txt', 'staticFeatureMatrixManual.csv')
    # getAccuracy('spam_words.txt', 'staticFeatureMatrixGiven2.csv')
    getAccuracy('scratch.txt', 'staticFeatureMatrixFull200.csv')
main()