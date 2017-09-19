from elasticsearch import Elasticsearch
import time
import math
from elasticsearch_dsl import Search
import random
import Canonicalizer
import decimal

decimal.getcontext().prec = 10

graphPages = {}
class Page:
    def __init__(self, page, auth, hub, inLinkPages, outLinkPages):
        self.page = page
        self.auth = auth
        self.hub = hub
        self.inLinkPages = inLinkPages
        self.outLinkPages = outLinkPages

    def setAuth(self, value):
        self.auth = value

    def setHub(self, value):
        self.hub = value

    def setoutLinkPages(self, value):
        self.outLinkPages = value

    def setinLinkPages(self, value):
        self.inLinkPages = value

rootSet = set()
baseSet = set()
es = Elasticsearch()
linkgraphTemp = {}
linkGraph = {}
sinkNodes = set()
start_time = time.time()
s = Search(using=es, index="hw3_crawl", doc_type='document')
s = s.source([])
docID = set(h.meta.id for h in s.scan())

page = es.search(
  index = 'hw3_crawl',
  doc_type = 'document',
  size = 1000,
  body = {
    "query": {
        "match": {
            "text": "United States battles won in WW2"
            }
        }
    })

for p in page['hits']['hits']:
    rootSet.add(p.get('_id'))
    baseSet.add(p.get('_id'))
    outlinks = set(p.get('_source').get("outlinks").strip().split('\n'))
    for ol in outlinks:
        if ol in docID:
            baseSet.add(ol)

with open("linkgraph.txt", 'r') as textFile:
    textFile.seek(0)
    dSet = set()
    flag = 1
    for line in textFile.readlines():
        pages = line.replace(' \n', '').replace('\n', '').split(' ')
        for link in rootSet:
            if (pages[0] == link):
                flag += 1
                for il in pages[1:]:
                    dSet.add(il)
        if(flag == 1000):
            break
    if len(dSet) <= 500:
        baseSet = baseSet.union(dSet)
    else:
        dSet = random.sample(dSet, 500)
    textFile.close()

print(len(baseSet))


for link in baseSet:
    olSet = set()
    res = es.get(index="hw3_crawl", doc_type='document', id=link)
    outLinks = set(res['_source'].get("outlinks").strip().split('\n'))
    for ol in outLinks:
        if ol in graphPages:
            olSet.add(ol)
    graphPages[link] = Page(link, 1.0, 1.0, set(), olSet)

print(len(graphPages))
with open("linkgraph.txt", 'r') as textFile:
    for line in textFile.readlines():
        plSet = set()
        pages = line.replace(' \n', '').replace('\n', '').split(' ')
        for link in baseSet:
            if (pages[0] == link):
                for p in pages[1:]:
                    if p in graphPages:
                        plSet.add(p)
                graphPages[link].setinLinkPages(plSet)
                break

# for link in graphPages:
#     print(link)
#     print(graphPages[link].outLinkPages)

print(len(graphPages)) #10642

def perplexity(entropy):
    return (pow(2, decimal.Decimal(entropy)))


def entropy(rank):
    if rank <= 0:
        return 0
    entropy = rank * float(math.log(rank, 2))
    return entropy

def hubs():
    totalAuth = 0
    totalAuthEntropy = 0
    totalHubEntropy = 0
    totalHub = 0
    for p in graphPages:
        for q in graphPages[p].inLinkPages:
            graphPages[p].auth += graphPages[q].hub
        for r in graphPages[p].outLinkPages:
            graphPages[p].hub += graphPages[r].auth
        totalHub += graphPages[p].hub
        totalAuth += graphPages[p].auth

    for p in graphPages:
        graphPages[p].hub = graphPages[p].hub / totalHub
        totalHubEntropy += entropy(graphPages[p].hub)
    # totalHubEntropy = 0
    # totalAuthEntropy = 0
    # norm = 0
    # for p in graphPages:
    #     # print(graphPages[p].hub)
    #     graphPages[p].setHub(0)
    #     # print(graphPages[p].hub)
    #     for r in graphPages[p].outLinkPages:
    #         graphPages[p].hub += graphPages[r].auth
    #     norm += graphPages[p].hub * graphPages[p].hub
    # normHub = math.sqrt(norm)
    #
    # for p in graphPages:
    #     graphPages[p].setHub(graphPages[p].hub / normHub)
    #     totalHubEntropy += entropy(graphPages[p].hub)
    return perplexity(-totalHubEntropy)



def auth():
    totalAuth = 0
    totalAuthEntropy = 0
    totalHubEntropy = 0
    totalHub = 0
    for p in graphPages:
        for q in graphPages[p].inLinkPages:
            graphPages[p].auth += graphPages[q].hub
        for r in graphPages[p].outLinkPages:
            graphPages[p].hub += graphPages[r].auth
        totalHub += graphPages[p].hub
        totalAuth += graphPages[p].auth

    for p in graphPages:
        graphPages[p].auth = graphPages[p].auth / totalAuth
        totalAuthEntropy += entropy(graphPages[p].auth)
    # norm = 0
    # totalAuthEntropy = 0
    # for p in graphPages:
    #     graphPages[p].setAuth(0)
    #     for q in graphPages[p].inLinkPages:
    #         graphPages[p].auth += graphPages[q].hub
    #     norm += graphPages[p].auth * graphPages[p].auth
    # normAuth = math.sqrt(norm)
    # for p in graphPages:
    #     graphPages[p].setAuth(graphPages[p].auth / normAuth)
    #     totalAuthEntropy += entropy(graphPages[p].auth)
    return perplexity(-totalAuthEntropy)

def HubsAndAuthority():
    # totalAuth = 0
    # totalAuthEntropy = 0
    # totalHubEntropy =0
    # totalHub = 0
    # for p in graphPages:
    #     for q in graphPages[p].inLinkPages:
    #         graphPages[p].auth += graphPages[q].hub
    #     for r in graphPages[p].outLinkPages:
    #         graphPages[p].hub += graphPages[r].auth
    #     totalHub += graphPages[p].hub
    #     totalAuth += graphPages[p].auth
    #
    # for p in graphPages:
    #     graphPages[p].auth = graphPages[p].auth/totalAuth
    #     totalAuthEntropy += entropy(graphPages[p].auth)
    #     graphPages[p].hub = graphPages[p].hub/totalHub
    #     totalHubEntropy += entropy(graphPages[p].hub)


    norm = 0
    totalHubEntropy = 0
    totalAuthEntropy = 0
    for p in graphPages:
        graphPages[p].setAuth(0)
        for q in graphPages[p].inLinkPages:
            graphPages[p].auth += graphPages[q].hub
        norm += graphPages[p].auth * graphPages[p].auth
    normAuth = math.sqrt(norm)
    for p in graphPages:
        graphPages[p].setAuth(graphPages[p].auth/normAuth)
        totalAuthEntropy += entropy(graphPages[p].auth)
    norm = 0
    for p in graphPages:
        # print(graphPages[p].hub)
        graphPages[p].setHub(0)
        # print(graphPages[p].hub)
        for r in graphPages[p].outLinkPages:
            graphPages[p].hub += graphPages[r].auth
        norm += graphPages[p].hub * graphPages[p].hub
    normHub = math.sqrt(norm)

    for p in graphPages:
        graphPages[p].setHub(graphPages[p].hub/normHub)
        totalHubEntropy += entropy(graphPages[p].hub)
    # return perplexity(-totalHubEntropy), perplexity(-totalAuthEntropy)

hubConvergence = 0
authConvergence = 0
round = 0
prevAuthPerplexity = 0
prevHubPerplexity = 0
k = 0
prevHub = 0
prevAuth = 0

while k < 50:
    HubsAndAuthority()
    k+=1
# while hubConvergence < 4:
#     curHubPerplexity = hubs()
#     if (abs((curHubPerplexity - prevHubPerplexity)) < 1):
#         hubConvergence += 1
#     else:
#         hubConvergence = 0
#     round += 1
#     print(round)
#     prevHubPerplexity = curHubPerplexity


# while hubConvergence < 4 and authConvergence < 4:
#     curHubPerplexity, curAuthPerplexity = HubsAndAuthority()
#     if (abs((curHubPerplexity - prevHubPerplexity)) < 1):
#         hubConvergence += 1
#     else:
#         hubConvergence = 0
#     if (abs((curAuthPerplexity - prevAuthPerplexity)) < 1):
#         authConvergence += 1
#     else:
#         authConvergence = 0
    # if (abs((curHubPerplexity - prevHubPerplexity)) < 1) and (abs((curAuthPerplexity - prevAuthPerplexity)) < 1):
    #     convergence += 1
    # else:
    #     convergence = 0
    # round += 1
    # print(round)
    # prevHubPerplexity = curHubPerplexity
    # prevAuthPerplexity = curAuthPerplexity
    # HubsAndAuthority()
    # k +=1
    # if(hub == prevHub) and (auth == prevAuth):
    #     convergence += 1
    # else:
    #     convergence = 0
    # prevAuth = auth
    # prevHub = hub

with open("hub.txt", 'a+') as textFile:
    pagesByRank = sorted(graphPages, key=lambda x: graphPages[x].hub)
    pageIndex = 0
    for page in reversed(pagesByRank):
        if (pageIndex >= 500):
            break
        textFile.write('%s %f %d\n' % (page, graphPages[page].hub, len(graphPages[page].outLinkPages)))
        pageIndex += 1
    textFile.close()


# print 'Total authorities score:', auth_score

# round = 0
# while authConvergence < 4:
#     curAuthPerplexity = auth()
#     if (abs((curAuthPerplexity - prevAuthPerplexity)) < 1):
#         authConvergence += 1
#     else:
#         authConvergence = 0
#     round += 1
#     print(round)
#     prevAuthPerplexity = curAuthPerplexity

with open("authority.txt", 'a+') as textFile:
    pagesByRank = sorted(graphPages, key=lambda x: graphPages[x].auth)
    pageIndex = 0
    for page in reversed(pagesByRank):
        if (pageIndex >= 500):
            break
        textFile.write('%s %f %d\n' % (page, graphPages[page].auth, len(graphPages[page].inLinkPages)))
        pageIndex += 1
    textFile.close()

temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))





