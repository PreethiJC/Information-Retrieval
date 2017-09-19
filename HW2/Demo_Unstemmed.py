from stemming.porter2 import stem
import time
from bs4 import BeautifulSoup
import os
import re
import regex
from collections import defaultdict
from collections import OrderedDict
import dill

def unpickler(file):
    f = open(file, 'rb')
    ds = dill.load(f)
    f.close()
    return ds

def parseCatalog(file):
    catalog = {}
    catalogFile = open(file, 'r')
    for line in catalogFile.readlines():
        content = line.strip().split(',')
        catalog[content[0]] = content[1:]
    return catalog

docInfo = unpickler('Files/Unstemmed/Pickles/docInfo.p')
catalog = parseCatalog('Files/Unstemmed/catalogFile.txt')
termMap = unpickler('Files/Unstemmed/Pickles/termMap.p')
docMap = unpickler('Files/Unstemmed/Pickles/docMap.p')

inFile = open("in.0.50.txt", "r")
indexFile = open("Files/Unstemmed/invertedFile0.txt", "r")
outFile = open("Files/out.0.no.stop.no.stem.txt", "a+")
for line in inFile.readlines():
    key = line.strip()
    keyId = str(termMap.get(key))
    if keyId in catalog.keys():
        offset = catalog[keyId][0]
        length = catalog[keyId][1]
        indexFile.seek(int(offset))
        termLine = indexFile.read(int(length))
        df = termLine.split(':')[0].split(',')[1]
        ttf = termLine.split(':')[0].split(',')[2]
        outLine = line.strip() + " " + df + " " + ttf+"\n"
        outFile.write(outLine)
    else:
        outFile.write(line)

outFile.close()
inFile.close()
indexFile.close()

