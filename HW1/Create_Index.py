import time
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import os
import re
from collections import Counter
import dill

es = Elasticsearch()
path = "/Users/Zion/Downloads/AP_DATA/ap89_collection/"
start_time = time.time()
i = 0
for filename in os.listdir(path):
    #if (filename == 'ap890130'):
    if(filename != 'readme'):
        file = open(path+filename)
        page = file.read()
        #docNo = []
        validPage = "<root>" + page + "</root>"
        soup = BeautifulSoup(validPage, 'xml')
        docs = soup.find_all('DOC')
        for doc in docs:

            i+=1
            texts = doc.find_all('TEXT')
            text = ""
            for txt in texts:
                text += txt.get_text()
            count = 0
            for line in text.splitlines():
                word = re.sub('\s+', ' ', line).strip().split(' ')
                count += len(word)
            jsonDoc = {
                    'text': text
            }
            #docNo.append(doc.DOCNO.get_text().strip())
            res = es.index(index="index1", doc_type='document', id=doc.DOCNO.get_text().strip(), body=jsonDoc)
            print("Indexed %d document" % i)
# f = open("Pickles/docIDs.txt", "wb")
# dill.dump(docNo, f)
# f.close()

temp = time.time()-start_time
print(temp)
hours = temp//3600
temp = temp - 3600*hours
minutes = temp//60
seconds = temp - 60*minutes
print('%d:%d:%d' %(hours,minutes,seconds))


