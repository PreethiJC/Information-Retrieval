from collections import OrderedDict
import math

relevanceJudgements = {}
def retrieveQueryResults(rankList):
    queryResults = OrderedDict()
    with open(rankList, 'r') as f:
        for queryResult in f:
            # items = queryResult.split('\t')
            items = queryResult.split(' ')
            queryID = items[0]
            documentID = items[2]
            if queryID in queryResults:
                queryResults[queryID].append(documentID)
            else:
                queryResults[queryID] = [documentID]
    f.close()
    return queryResults

def getRevelanceJudgements(qrel):
    with open(qrel, 'r') as f:
        for judgement in f:
            # cols = judgement.split('\t')
            cols = judgement.split(' ')
            queryID = cols[0]
            documentID = cols[2]
            relevance = cols[3].strip()
            if relevance == '1':
                if queryID in relevanceJudgements:
                    relevanceJudgements[queryID].append(documentID)
                else:
                    relevanceJudgements[queryID] = [documentID]
    f.close()

def getScoreForID(queryID, documents):
    relevanceScore = []
    relevantDocuments = []
    if queryID in relevanceJudgements:
        relevantDocuments = relevanceJudgements[queryID]
    for document in documents:
        if document in relevantDocuments:
            relevanceScore.append(1)
        else:
            relevanceScore.append(0)
    return relevanceScore

def designateVals(lst, val, rank):
    if rank in lst:
        lst[rank].append(val)
    else:
        lst[rank] = [val]
    return lst

def printMeanVals(lst, desc, kVals=[], qid=''):
    if not kVals:
        print(desc + ': ' + str("{:.4f}".format(math.fsum(lst) / len(lst))))
    else:
        for k in kVals:
            if qid != '':
                print(desc + str(k) + ' for ' + qid + ': ' + str("{:.4f}".format(math.fsum(lst[k]) / len(lst[k]))))
            else:
                print(desc + str(k) + ': ' + str("{:.4f}".format(math.fsum(lst[k]) / len(lst[k]))))

def calculateMetrics(queryResults, option):
    kVals = [5, 10, 20, 50, 100]
    qid = 0
    AP, RP, NDCG = [], [], []
    P, R, F1 = {}, {}, {}
    f = open("details.txt", 'w')
    for queryID in queryResults:
        qid += 1
        relevanceScore = []
        PTemp, RTemp, F1Temp = {}, {}, {}
        psum, rank, relevantNumber, rp = 0, 0, 0, 0
        results = queryResults[queryID]
        if queryID in relevanceJudgements:
            relevantDocuments = relevanceJudgements[queryID]
        else:
            continue
        for document in results:
            rank += 1
            isRelevant = 0
            if document in relevantDocuments:
                relevantNumber += 1
                isRelevant = 1
            if(rank <= len(relevantDocuments)):
                rp = relevantNumber
            precision = relevantNumber / (rank * 1.0)
            if isRelevant == 1:
                psum += precision
            recall = 0 if len(relevantDocuments) == 0 else relevantNumber / (len(relevantDocuments) * 1.0)
            if rank in kVals:
                P = designateVals(P, precision, rank)
                PTemp = designateVals(PTemp, precision, rank)
                if (relevantNumber > 0):
                    f1 = (2 * precision * recall) / (precision + recall)
                else:
                    f1 = 0
                F1 = designateVals(F1, f1, rank)
                F1Temp = designateVals(F1Temp, f1, rank)
                R = designateVals(R, recall, rank)
                RTemp = designateVals(RTemp, recall, rank)

            relevanceScore.append(isRelevant)
            f.write(queryID + ' ' + document + ' ' + str(rank) + ' ' + str(isRelevant) + ' ' + str(
                "{:.4f}".format(precision)) + ' ' + str("{:.4f}".format(recall)) + '\n')
        j = 0
        dc_value = 0.0
        for score in relevanceScore:
            j+=1
            dc_value += (score) / math.log((1.0 + j))
        j = 0
        idc_value = 0.0
        relevanceScore = sorted(relevanceScore, reverse=True)
        for score in relevanceScore:
            j+=1
            idc_value += (score) / math.log((1.0 + j))
        rPrecision = rp/len(relevantDocuments)
        RP.append(rPrecision)
        if idc_value == 0.0:
            ndcg = 0.0
        else:
            ndcg = dc_value / idc_value

        NDCG.append(ndcg)

        avgPrecision = 0.0
        if relevantNumber != 0:
            avgPrecision = psum / (len(relevantDocuments) * 1.0)
        AP.append(avgPrecision)
        if(option == 1):
            print('Average Precision for ' + queryID + ': ' + str("{:.4f}".format(avgPrecision)))
            print('R-precision for ' + queryID + ': ' + str("{:.4f}".format(rPrecision)))
            print('nDCG for ' + queryID + ': ' + str("{:.4f}".format(ndcg)) + '\n')
            print('Precision@ Values')
            printMeanVals(PTemp, 'Mean Precision@', kVals, queryID)
            print('\nRecall@ Values')
            printMeanVals(RTemp, 'Mean Recall@', kVals, queryID)
            print('\nF1@ Values')
            printMeanVals(F1Temp, 'Mean F1@', kVals, queryID)
            print('\n')

    printMeanVals(AP, 'Average Precision')
    printMeanVals(RP, 'R-precision')
    printMeanVals(NDCG, 'nDCG')
    print('\nPrecision@ Values')
    printMeanVals(P, 'Mean Precision@', kVals)
    print('\nRecall@ Values')
    printMeanVals(R, 'Mean Recall@', kVals)
    print('\nF1@ Values')
    printMeanVals(F1, 'Mean F1@', kVals)
    f.close()

def main():
    cmd = input('Enter command: ')
    cmd_params = cmd.split(' ')
    if len(cmd_params) == 4:
        # trec_eval [-q] qrels.txt rankList.txt
        # trec_eval [-q] qrels.adhoc.51-100.AP89.txt OkapiBM25_Results_File.txt

        queryResults = retrieveQueryResults(cmd_params[3])
        getRevelanceJudgements(cmd_params[2])
        calculateMetrics(queryResults, 1)
    else:
        # trec_eval qrels.txt rankList.txt
        # trec_eval qrels.adhoc.51-100.AP89.txt OkapiBM25_Results_File.txt
        # trec_eval qrels.adhoc.51-100.AP89.txt OkapiTF_Results_File.txt
        # trec_eval qrels.adhoc.51-100.AP89.txt UnigramLMJM_Results_File.txt
        # trec_eval qrels.adhoc.51-100.AP89.txt UnigramLMLaplace_Results_File.txt
        # trec_eval qrels.adhoc.51-100.AP89.txt TF-IDF_Results_File.txt
        queryResults = retrieveQueryResults(cmd_params[2])
        getRevelanceJudgements(cmd_params[1])
        calculateMetrics(queryResults, 2)
main()