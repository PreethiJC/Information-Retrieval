
def retriveDocs(k):
    f = open('Files/OkapiBM25_Results_File.txt', 'r')
    docNo = []
    i = 0
    for line in f:
        #print("a" + line.split()[3].strip() + "a")
        if(i < k):
            i+=1
            docNo.append(line.split()[2])
    return docNo

print(retriveDocs(10))

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
            if doc_id not in docScoreDict:
                docScoreDict[doc_id] = 0.0
            docScoreDict[doc_id] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)

    with open('Files/UnigramLMLaplace_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %f Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1

def JM_BackgroundSmoothing(termVector, key):
    pML = 0
    docLen = 1
    for docid in termVector:
        if key in termVector[docid].get(key, {}):
            tf = termVector[docid][key][0]
            docLen = termVector[docid][key][1]
        else:
            tf = 0
        pML += tf/docLen
    pML /= D
    return pML

def UnigramLM_JelinekMercer(qNo, termVector):
    keys = set()
    for doc_id in termVector:
        for key in termVector[doc_id]:
            keys.add(key)
    keys = list(keys)
    l = 0.2
    docScoreDict = {}
    for word in keys:
        for docid in termVector:
            dict = termVector[docid]
            if word in dict:
                tfwd = dict[word][0]
                docLen = dict[word][1]
                pML = (filter(lambda x: x[1] == word, cTF)[0][0]) / V
                # JM_BackgroundSmoothing(termVector, key)
                score = float(l * float(tfwd / docLen)) + (float(1 - l) * pML)
                #score = float(tfwd + 1) / float(docLen + V)
            else:
                docLen = dict[dict.keys()[0]][1]
                pML = (filter(lambda x: x[1] == word, cTF)[0][0]) / V
                score = (float(1 - l) * pML)
            if doc_id not in docScoreDict:
                docScoreDict[doc_id] = 0.0
            docScoreDict[doc_id] += math.log(score)
    DocScore = []
    for score_key in docScoreDict.keys():
        DocScore.append((score_key, docScoreDict[score_key]))
    DocScore.sort(key=itemgetter(1), reverse=True)
    #print(docScore)
    with open('Files/UnigramLMJM_Results_File.txt', 'a+') as queryResults:
        rank = 1
        for ds in DocScore:
            queryResults.write('%s Q0 %s %d %lf Exp\n' % (qNo, ds[0], rank, ds[1]))
            if rank == 1000:
                break
            rank += 1