
import math
import decimal

decimal.getcontext().prec = 10
graphPages = {}
d = 0.85


class Page:
    def __init__(self, page, rank, inLinkPages, noOfOutLinks):
        self.page = page
        self.rank = rank
        self.inLinkPages = inLinkPages
        self.noOfOutLinks = noOfOutLinks

    def setRank(self, value):
        self.rank = value

    def setnoOfOutLinks(self, value):
        self.noOfOutLinks = value

    def setinLinkPages(self, value):
        self.inLinkPages = value


def getSinkNodes():
    return {k: v for k, v in graphPages.items() if v.noOfOutLinks == 0}

def countInlink():
    return {k: v for k, v in graphPages.items() if len(v.inLinkPages) > 0}

def getSourceNodes():
    return {k: v for k, v in graphPages.items() if len(v.inLinkPages) == 0}

def countOutlink():
    return {k: v for k, v in graphPages.items() if v.noOfOutLinks > 0}

def getOutLinks(page):
    return {k: v for k, v in graphPages.items() if page in v.inLinkPages}


def perplexity(entropy):
    return (pow(2, decimal.Decimal(entropy)))


def entropy(rank):
    entropy = rank * float(math.log(rank, 2))
    return entropy


def initializegraphPages(graphFile):
    with open(graphFile, 'r') as textFile:
        for line in textFile.readlines():
            if line == '' or line == 's' or line == '\n':
                continue
            pages = line.replace(' \n', '').replace('\n', '').split(' ')

            if (pages[0] != '' and pages[0] != 's'):
                if pages[0] in graphPages:
                    graphPages[pages[0]].setinLinkPages(pages[1:len(pages)])
                else:
                    graphPages[pages[0]] = (Page
                                            (pages[0], (float(1) / len(pages)),
                                             pages[1:len(pages)], 0))
            for restPage in pages[1:len(pages)]:
                if (restPage != '' and restPage != 's'):
                    if restPage in graphPages:
                        graphPages[restPage].noOfOutLinks += 1
                    else:
                        graphPages[restPage] = (Page
                                                (pages[0], (float(1) / len(pages)),
                                                 [], 1))

def calculatePageRank(sinkNodes):
    sinkPR = 0
    for node in sinkNodes:
        sinkPR += graphPages[node].rank

    pageIndex = 0
    totalEntropy = 0
    noOfPages = len(graphPages)

    for page in graphPages:
        newPR = (1 - d) / noOfPages
        newPR += d * sinkPR / noOfPages
        inLinks = graphPages[page].inLinkPages
        for link in inLinks:
            newPR += d * graphPages[link].rank / graphPages[link].noOfOutLinks
        graphPages[page].setRank(newPR)
        totalEntropy += entropy(newPR)
    return perplexity(-totalEntropy)


initializegraphPages("wt2g_inlinks.txt")
sinkNodes = getSinkNodes()
print("Sink Nodes: %d" %len(sinkNodes))
for sn in sinkNodes:
    print(sn)
sourceNodes = getSourceNodes()
inLinkCount = countInlink()
ouLinkCount = countOutlink()

convergence = 0
round = 0
prevPerplexity = 0
curPerplexity = 0
while convergence < 4:
    curPerplexity = calculatePageRank(sinkNodes)
    if abs((curPerplexity - prevPerplexity)) < 1:
        convergence += 1
    else:
        convergence = 0
    round += 1
    prevPerplexity = curPerplexity
print("Number of rounds: %d" %round)
#
with open("wt2g_rank.txt", 'a+') as textFile:
    pagesByRank = sorted(graphPages, key=lambda x: graphPages[x].rank)
    pageIndex = 0
    for page in reversed(pagesByRank):
        if (pageIndex >= 500):
            break
        textFile.write('%s %f %d\n' % (page, graphPages[page].rank, len(graphPages[page].inLinkPages)))
        pageIndex += 1
    textFile.close()
