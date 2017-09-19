import os
import email
from bs4 import BeautifulSoup
import re

Files = os.listdir("Files/")
for file in Files:
    with open("Files/" + file, 'r', encoding="ISO-8859-1") as f:
        # if(file != '.DS_Store'):
        #     print(file)
        #     line = f.readline()
        #     tag = line.rsplit('/', 1)[1].replace('EMAIL>\n', '/EMAILID>\n')
        #     line = line.rsplit('/', 1)[0]+tag
        #     rest = f.read()
        #     with open("Files/" + file, 'w') as wf:
        #         wf.writelines(line+rest)
        #     wf.close()
    f.close()

