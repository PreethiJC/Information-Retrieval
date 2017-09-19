import dill

def unpickler(file):
    f = open(file, 'rb')
    ds = dill.load(f)
    f.close()
    return ds
docInfo = unpickler('Files/Stemmed/Pickles/docInfo.p')

print len(docInfo)