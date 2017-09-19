import pandas
from sklearn import model_selection
from sklearn import linear_model
from operator import itemgetter

from operator import itemgetter

def createDict(qdIDTest, predictions):
    testDict = {}
    i = 0
    for prediction in predictions:
        qdIDVal = qdIDTest[i][0]
        i += 1
        qID = qdIDVal.split('-', 1)[0]
        docID = qdIDVal.split('-', 1)[1]
        if qID in testDict:
            testDict[qID].append((docID, prediction))
        else:
            testDict[qID] = []
            testDict[qID].append((docID, prediction))
    return testDict

def sortDict(testDict):
    for item in testDict:
        sorted_list = sorted(testDict[item], key=itemgetter(1))
        testDict[item] = sorted_list
    return testDict

def createPerformanceFile(testDict):
    with open('trainingperformance.txt', 'a') as f:
        i = 0
        for item in testDict:
            i = 0
            for docScorePair in testDict[item]:
                i+=1
                f.write("%s Q0 %s %d %f Exp\n" %(item, docScorePair[0], i, docScorePair[1]))
    f.close()

def main():
    qID_docID = ['QID-DocID']

    df = pandas.read_csv('staticFeatureMatrix.csv', skipinitialspace=True, usecols=qID_docID) #contains query ID and doc ID
    df_array = df.values
    qdID = df_array

    names = ['TF-IDF', 'Okapi TF', 'BM25', 'Laplace', 'Jelinek-Mercer', 'Label']
    dataset = pandas.read_csv('staticFeatureMatrix.csv', names=names, skiprows=[0]) #contains retrieval model scores and label
    array = dataset.values
    X = array[:,0:5] #contains only retrieval model scores
    Y = array[:,5]#contains only label

    kfold = model_selection.KFold(n_splits=5, random_state=None, shuffle=False) #k-fold cross validation
    for train, test in kfold.split(X, Y):
        qdIDTest = qdID[train]
        regr = linear_model.LinearRegression()
        regr.fit(X[train], Y[train]) #train
        predictions = regr.predict(X[train]) #predict
        # print(len(predictions))

        testDict = createDict(qdIDTest, predictions)
        testDict = sortDict(testDict)
        createPerformanceFile(testDict)

main()

