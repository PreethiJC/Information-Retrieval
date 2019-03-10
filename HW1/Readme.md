# HW1

Implement and compare various retrieval systems using vector space models and language models.

This assignment will also introduce elasticsearch: one of the many available commercial-grade indexes. 

This assignment involves writing two programs:

1. A program to parse the corpus and index it with elasticsearch
2. A query processor, which runs queries from an input file using a selected retrieval model

## Getting Started
* Download and install [elasticsearch](https://www.elastic.co), and the [kibana](https://www.elastic.co/products/kibana) plugin
* Download [AP89_DATA.zip](http://dragon.ischool.drexel.edu/example/ap89_collection.zip).

## Document Indexing
Create an index of the downloaded corpus (AP89_Collection). **CreateIndex.py** is a program to parse the documents and send them to my elasticsearch instance.

The corpus files are in a standard format used by TREC. Each file contains multiple documents. The format is similar to XML, but standard XML and HTML parsers will not work correctly. Instead, read the file one line at a time with the following rules:

1. Each document begins with a line containing ```<DOC>``` and ends with a line containing ```</DOC>```.
2. The first several lines of a document’s record contain various metadata. You should read the ```<DOCNO>``` field and use it as the ID of the document.
3. The document contents are between lines containing ```<TEXT>``` and ```</TEXT>```.
4. All other file contents can be ignored.  

Term positions are indexed as they are needed later. 

## Query execution
**Query_Processing.py** and **Retrieval_Models.py** are the programs that prep and run the queries in the file query_desc.51-100.short.txt, included in the data .zip file. All queries (omitting the leading number) are executed using each of the retrieval models listed below, and the top 100 results for each query is written to an output file. If a particular query has fewer than 100 documents with a nonzero matching score, then whichever documents have nonzero scores are listed.

One output file per retrieval model must be generated. Each line of an output file should specify one retrieved document, in the following format:

```<query-number> Q0 <docno> <rank> <score> Exp```  

Where:

* *query-number* is the number preceding the query in the query list
* *docno* is the document number, from the ```<DOCNO>``` field (which we asked you to index)
* *rank* is the document rank: an integer from 1-1000
* *score* is the retrieval model’s matching score for the document
* *Q0* and *Exp* are entered literally

**Query_Processing.py** will run queries against elasticsearch. Instead of using their built in query engine, the program will be retrieving information such as TF and DF scores from elasticsearch and implementing our own document ranking. 

**Retrieval_Models.py** implements the following retrieval models, using TF and DF scores from your elasticsearch index, as needed.

### ES built-in
Use ES query with the API ```"match"{"body_text":"query keywords"}```. This should be somewhat similar to BM25 scoring

### Okapi TF
This is a vector space model using a slightly modified version of TF to score documents. The Okapi TF score for term *w* in document *d* is as follows.

>![alt-text](https://latex.codecogs.com/gif.latex?okapi\\_tf(w,d)&space;=&space;\frac{tf_{w,d}}{tf_{w,d}&plus;0.5&plus;1.5(\frac{len(d)}{avg(len(d))})})


Where:

* ![alt-text](https://latex.codecogs.com/gif.latex?{tf_{w,d}})&nbsp;&nbsp;is the term frequency of term *w* in document *d*
* ![alt-text](https://latex.codecogs.com/gif.latex?{len(d)})&nbsp;&nbsp;is the length of document *d*
* ![alt-text](https://latex.codecogs.com/gif.latex?{avg(len(d))})&nbsp;&nbsp;is the average document length for the entire corpus  

The matching score for document *d* and query *q* is as follows.

>![alt-text](https://latex.codecogs.com/gif.latex?tf(d,q)=\sum_{w\in&space;q}&space;okapi\\_tf(w,d))

### TF-IDF
This is the second vector space model. The scoring function is as follows.

>![alt-text](https://latex.codecogs.com/gif.latex?tfidf(d,q)=\sum_{w\in&space;q}&space;okapi\_tf(w,d)*log&space;\frac{D}{df_w})  

Where:

* ![alt-text](https://latex.codecogs.com/gif.latex?{D})&nbsp;&nbsp;is the total number of documents in the corpus
* ![alt-text](https://latex.codecogs.com/gif.latex?{df_w})&nbsp;&nbsp;is the number of documents which contain term w

### Okapi BM25
BM25 is a language model based on a binary independence model. Its matching score is as follows.

>![alt-text](https://latex.codecogs.com/gif.latex?bm25(d,q)=\sum_{w\in&space;q}&space;\left&space;[&space;log&space;\left&space;(\frac{D&plus;0.5}{df_w&plus;0.5}&space;\right&space;)*\frac{tf_{w,d}&plus;k_1*tf_{w,d}}{tf_{w,d}&plus;k_1\left&space;(&space;(1-b)&plus;b*\frac{len(d)}{avg(len(d))}&space;\right&space;)}&space;*\frac{tf_{w,q}&plus;k_2*tf_{w,q}}{tf_{w,q}&plus;k_2}\right&space;])  

Where:
* ![alt-text](https://latex.codecogs.com/gif.latex?{tf_{w,q}})&nbsp;&nbsp;is the term frequency of term *w* in query *q*
* ![alt-text](https://latex.codecogs.com/gif.latex?{k_1})&nbsp;, ![alt-text](https://latex.codecogs.com/gif.latex?{k_2})&nbsp;, and ![alt-text](https://latex.codecogs.com/gif.latex?{b})&nbsp;&nbsp;are constants. 

### Unigram LM with Laplace smoothing
This is a language model with Laplace (“add-one”) smoothing. We will use maximum likelihood estimates of the query based on a multinomial model “trained” on the document. The matching score is as follows.

>![alt-text](https://latex.codecogs.com/gif.latex?lm\\_laplace(d,q)=\sum_{w\in&space;q}&space;log&space;(p\\_laplace(w|d))) 
>
>![alt-text](https://latex.codecogs.com/gif.latex?p\\_laplace(w|d)=\frac&space;{tf_{w,d}&plus;1}{len(d)&plus;V})  

Where:

* ![alt-text](https://latex.codecogs.com/gif.latex?{V})&nbsp;&nbsp;is the vocabulary size – the total number of unique terms in the collection.

### Unigram LM with Jelinek-Mercer smoothing
This is a similar language model, except that here we smooth a foreground document language model with a background model from the entire corpus.

>![alt-text](https://latex.codecogs.com/gif.latex?lm\\_jm(d,q)=\sum_{w\in&space;q}log(p\\_jm(w|d)))
>
>![alt-text](https://latex.codecogs.com/gif.latex?p\\_jm(w|d)=\lambda&space;\frac{tf_{w,d}}{len(d)}&space;&plus;&space;(1-\lambda)\frac{\sum_{{d}'}&space;tf_{w,{d}'}}{\sum_{{d}'}len({d}')})  

Where:

* ![alt-text](https://latex.codecogs.com/gif.latex?\lambda&space;\in&space;(0,1))&nbsp;&nbsp;is a smoothing parameter which specifies the mixture of the foreground and background distributions.  

Estimated the corpus probability using ![alt-text](https://latex.codecogs.com/gif.latex?\frac{cf_w}{V}).

## Evaluation
1. Compare manually the top 10 docs returned by ESBuilt-In, TFIDF, BM25, LMJelinek, for any 5 queries.

2. Download [trec_eval](http://www.ccs.neu.edu/home/vip/teach/IRcourse/1_retrieval_models/HW1/trec_eval) and use it to evalute the results for each retrieval model.

To perform an evaluation, run:

```$ trec_eval [-q] qrel_file results_file```

The ```-q``` option shows a summary average evaluation across all queries, followed by individual evaluation results for each query; without the ```-q``` option, you will see only the summary average. The trec_eval program provides a wealth of statistics about how well the uploaded file did for those queries, including average precision, precision at various recall cut-offs, and so on.

You should evaluate using the QREL file named qrels.adhoc.51-100.AP89.txt, included in the data .zip file.
