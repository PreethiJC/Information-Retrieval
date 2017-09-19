from collections import OrderedDict
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Search

relevanceJudgements = {}
queries = [('Causes of world war 2', '151801'),
           ('Battles won by USA in World War 2', '151802'),
           ('Battle of Stalingrad', '151803')]

def parseRawQrel():
    i = 0
    n = 1
    with open('qrels-raw.txt', 'r') as f:
        for relevanceJudgement in f:
            if(i >= n):
                cols = relevanceJudgement.split('\t')
                queryID = cols[0]
                documentID = cols[2]
                if(len(cols)) > 5:
                    score = int(cols[3]) + int(cols[4]) + int(cols[5])
                else:
                    score = int(cols[3]) + int(cols[4])
                qArr = []
                qArr.append(queryID)
                qArr.append(documentID)
                if score in relevanceJudgements:
                    relevanceJudgements[score].append(qArr)
                else:
                    relevanceJudgements[score] = [qArr]
            i += 1
    f.close()


def createQrel():
    rJudge = OrderedDict(sorted(relevanceJudgements.items(), key=lambda t: t[0], reverse=True))
    with open('qrels.txt', 'w') as f:
        for score in rJudge:
            for ids in rJudge[score]:
                if score > 0:
                    s = '1'
                else:
                    s = str(score)
                line = ids[0] + " 0 " + ids[1] + " " + s + "\n"
                f.write(line)
    f.close()

def createRankList(query, id):
    es = Elasticsearch()
    s = Search().using(es).query("match", text=query)
    res = s[0:1000].execute()
    docInfo = [(h.meta.id, h.meta.score) for h in res.hits]
    i = 0
    with open('rankList.txt', 'a+') as f:
        for di in docInfo:
            i+=1
            line = id + " Q0 " + di[0] + " " + str(i) + " " + str(di[1]) + " " + "Exp\n"
            f.write(line)
    f.close()

def main():
    parseRawQrel()
    createQrel()
    for query in queries:
        createRankList(query[0], query[1])

main()