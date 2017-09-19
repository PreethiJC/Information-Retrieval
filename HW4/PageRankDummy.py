import urllib
import re
import os
import math
import operator
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


def getSourceNodes():
    return {k: v for k, v in graphPages.items() if len(v.inLinkPages) == 0}


def getOutLinks(page):
    return {k: v for k, v in graphPages.items() if page in v.inLinkPages}

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
            # print('%d' % len(pages))
            # print('%lf' % graphPages[pages[0]].rank)

initializegraphPages("LinkGraphDummy.txt")
sinkNodes = getSinkNodes()
sourceNodes = getSourceNodes()
print(sinkNodes)
print(sourceNodes)