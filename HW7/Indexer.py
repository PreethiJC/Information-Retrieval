import time
from elasticsearch import Elasticsearch
from bs4 import BeautifulSoup
import os
import re
from collections import Counter
import dill

es = Elasticsearch()
path = "Files/"
start_time = time.time()
i = 0
for filename in os.listdir(path):
    if(filename != '.DS_Store'):
        print(filename)
        file = open(path+filename, "r", encoding="ISO-8859-1")
        page = file.read()
        validPage = "<root>" + page + "</root>"
        soup = BeautifulSoup(validPage, 'html.parser')
        i += 1
        texts = soup.find_all('text')
        labels = soup.find_all('label')
        text = ""
        label = ""
        for txt in texts:
            text += txt.get_text().strip()
        for l in labels:
            label += l.get_text().strip()
        jsonDoc = {
            'text': text,
            'label': label
        }
        res = es.index(index="hw7_index", doc_type='document', id=soup.emailid.text.strip(), body=jsonDoc)
        print("Indexed %d document" % i)

temp = time.time() - start_time
print(temp)
hours = temp // 3600
temp = temp - 3600 * hours
minutes = temp // 60
seconds = temp - 60 * minutes
print('%d:%d:%d' % (hours, minutes, seconds))
