docID = set()
linkgraph = {}
lg = {}
sinkNodes = set()
g = open("graph.txt", "r")
for line in g.readlines():
    for ol in line.split(":")[1].split():
        docID.add(line.split(":")[0])
        if ol in linkgraph:
            linkgraph[ol].add(line.split(":")[0])
        else:
            linkgraph[ol] = set(line.split(":")[0])
print(docID)
for ol in linkgraph:
    if ol in docID:
        lg[ol] = linkgraph.get(ol)
    if ol == '':
        for link in linkgraph.get(ol):
            sinkNodes.add(link)

of = open("LinkGraphDummy.txt", "w")
for ol in lg:
    line = ol
    for il in lg[ol]:
        line += ' ' + il
    of.write(line + '\n')
of.close()

print(sinkNodes)
