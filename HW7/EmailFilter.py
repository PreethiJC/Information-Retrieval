import os
import email
from bs4 import BeautifulSoup
import re

path_to_data_files = '/Users/Zion/Downloads/trec07p/data/'
url = re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', re.I)


def spamHam():
    labelDict = {}
    with open('/Users/Zion/Downloads/trec07p/full/index', 'r') as indexFile:
        for line in indexFile.readlines():
            lineStr = line.split(' ')
            id = lineStr[1].rsplit('.', 1)[1].strip()
            label = lineStr[0]
            labelDict[id] = label
    indexFile.close()
    return labelDict

def getBody(parts):
    ret = []
    if type(parts) == str:
        ret.append(parts)
    elif type(parts) == list:
        for part in parts:
            if part.is_multipart():
                ret += getBody(part.get_payload())
            else:
                ret += getBody(part)
    elif parts.get_content_type().split(' ')[0] == 'text/plain':
        ret.append(parts.get_payload())
    elif parts.get_content_type().split(' ')[0] == 'text/html':
        soup = BeautifulSoup(parts.get_payload(), 'html.parser')
        email_content_string = soup.get_text()
        ret.append(email_content_string)
    return ret

def clean_string(input_string):

    cleaned_string = input_string.replace('-', ' ').replace('.', ' ').replace('?', ' ') \
        .replace('/', ' ').replace('!', ' ').replace('@', ' ').replace('#', ' ').replace(',', ' ') \
        .replace('%', ' ').replace(':', ' ').replace(';', ' ').replace('<', ' ').replace('>', ' ').replace('$', ' ')\
    .replace('*', ' ').replace('&', ' ').replace('_', ' ').replace('~', ' ').replace('[', ' ').replace(']', ' ')\
    .replace('(', ' ').replace(')', ' '). replace('\\', ' ').replace('{', ' ').replace('}', ' ').replace('^', ' ')\
    .replace('"', ' ').replace('\n', ' ').replace('=', ' ').replace('+', ' ')

    cleaned_string = ' '.join(cleaned_string.split())
    return cleaned_string

def load_trec_spam_files():
    labelDict = spamHam()
    total_files = os.listdir(path_to_data_files)
    for each_file in total_files:
        with open(path_to_data_files + each_file, 'r', encoding="ISO-8859-1") as Email_File:
            emailID = each_file.split('.')[1]
            msg = email.message_from_file(Email_File)
            subject = msg['Subject']
            body = '\n'.join(
                p for p in getBody(msg.get_payload())
                if type(p) == str
            )
            emailText =''
            if not subject:
                emailText += body
            elif not body:
                emailText += subject
            else:
                emailText = subject + '\n' + body

            emailText = url.sub(' ', emailText)
            emailText = clean_string(emailText)
            label = labelDict[emailID]
            with open('Files/%s.txt' %emailID, 'w') as eFile:
                content = "<EMAILID>%s</EMAILID>\n<TEXT>%s</TEXT>\n<LABEL>%s</LABEL>" %(emailID, emailText, label)
                eFile.write(content)
            eFile.close()
        Email_File.close()

load_trec_spam_files()