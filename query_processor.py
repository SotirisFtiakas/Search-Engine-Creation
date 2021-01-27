import pandas as pd
import numpy as np
import string
import math
from indexer import preprocessing, termFrequency, TF_Process, IDF_Process


# Function for query preprocessing
def query_Preprocessing(query):
    # Make all letters lowercase
    query = query.lower()

    # Remove punctuation
    query = query.translate(str.maketrans('', '', string.punctuation))

    # Remove stopwords
    f = open("stopwords.txt", "r")
    stopwords = f.read()

    query = ' '.join([word for word in query.split() if word not in stopwords])
    return query.split()


# Function to calculate TF for every term in every document
def query_TF_Process(query, data, globalDict):
    
    queryGlobalDict = globalDict.copy()
    TF={}   # Dictionary where:
                # key = term, 
                # value = TF in the query
    
    for term in query:
    
        if not term in queryGlobalDict:
            queryGlobalDict[term] = ["query"]
        elif not term in TF:
            doc_list = queryGlobalDict.get(term)
            doc_list.append("query")
            queryGlobalDict[term] = doc_list

        # calculate the TF    
        TF[term] = termFrequency(term,query,len(query))
    
    return queryGlobalDict, TF


# Function to calculate IDF for every term
def query_IDF_Process(query, queryGlobalDict, total_docs):
    queryDictionaryIDF = queryGlobalDict.copy()
    for i in query:
        queryDictionaryIDF[i] = 1 + math.log(float(total_docs/len(queryDictionaryIDF[i])))
    return queryDictionaryIDF


def cosine_formula(query, queryTF, queryIDF, queryTFIDF):
    dot_product=0
    query_norm=0
    doc_norm=0

    for i in query:
        dot_product += float(queryTFIDF[i]*(queryTF[i]*queryIDF[i]))
        query_norm += math.pow((queryTFIDF[i]),2)
        doc_norm += math.pow((queryTF[i]*queryIDF[i]),2)

    query_norm = math.sqrt(query_norm)
    doc_norm = math.sqrt(doc_norm)

    return (dot_product/query_norm*doc_norm)

def cosine_similarity(query, queryTFIDF, documentsTF, dictionaryIDF):
    similarity_matrix = [cosine_formula(query, documentsTF[j], dictionaryIDF, queryTFIDF) for j in range(len(documentsTF))]
    
    return similarity_matrix


if __name__ == "__main__":

    data = pd.read_csv("database.csv")
    preprocessing(data)
    globalDict, documentsTF = TF_Process(data)
    dictionaryIDF = IDF_Process(globalDict,data.shape[0]) 
    query = "Los unlimited favorito?"
    query = query_Preprocessing(query)
    queryGlobalDict, queryTF = query_TF_Process(query,data,globalDict)
    queryDictionaryIDF = query_IDF_Process(query, queryGlobalDict, data.shape[0])
    queryTFIDF={}
    for i in query:
        queryTFIDF[i] = queryDictionaryIDF[i]*queryTF[i]
    # fill documentsTF's documents' missing key:value pairs with key=key:value=0
    for i in dictionaryIDF.keys():
        for j in range(len(documentsTF)):
            if not i in documentsTF[j]:
                documentsTF[j][i]=0

    similarity_matrix = cosine_similarity(query, queryTFIDF, documentsTF, dictionaryIDF)
    query_data = data.copy()
    query_data['Score'] = np.array(similarity_matrix)
    query_data.sort_values(by=['Score'], inplace=True, ascending=False)
    print(query_data.head())

    