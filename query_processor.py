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
def query_IDF_Process(query, queryGlobalDict, dictionaryIDF, total_docs):
    queryDictionaryIDF = dictionaryIDF.copy()
    for i in query:
        queryDictionaryIDF[i] = 1 + math.log(float(total_docs/len(queryGlobalDict[i])))
    return queryDictionaryIDF


# def cosine_formula(query, queryTF, queryIDF, queryTFIDF):
#     dot_product=0
#     query_norm=0
#     doc_norm=0

#     for i in query:
#         dot_product += float(queryTFIDF[i]*(queryTF[i]*queryIDF[i]))
#         query_norm += math.pow((queryTFIDF[i]),2)
#         doc_norm += math.pow((queryTF[i]*queryIDF[i]),2)

#     query_norm = math.sqrt(query_norm)
#     doc_norm = math.sqrt(doc_norm)

#     return (dot_product/query_norm*doc_norm)


def cosine_similarity1(query_vector_list,tfidf_list):
    similarity_matrix = [cosine_formula1(query_vector_list,list(doc.values())) for doc in tfidf_list]
    return similarity_matrix

def cosine_formula1(query,doc):
    dot_product = np.dot(query,doc)
    query_norm = np.linalg.norm(query)
    doc_norm = np.linalg.norm(doc)

    return (dot_product/query_norm*doc_norm)

# def cosine_similarity(query, queryTFIDF, documentsTF, dictionaryIDF):
#     similarity_matrix = [cosine_formula(query, documentsTF[j], dictionaryIDF, queryTFIDF) for j in range(len(documentsTF))]
    
#     return similarity_matrix

def create_vector(single_doc, queryDictionaryIDF, queryGlobalDict):
    doc_tfidf = {}
    for term in queryGlobalDict.keys():
        doc_tfidf[term] = 0
    
    for term in queryGlobalDict.keys():
        if term in single_doc.keys():
            doc_tfidf[term] = single_doc[term]* queryDictionaryIDF[term]

    return doc_tfidf

def create_optimized_query(better, queries_df, full_query_vector):
    worse = [0,1,2,3,4,5,6]  # Hardcoded 7 Results
    a = 1       # Initial TFIDF
    b = 0.5     # + 0.5 of good pages TFIDFs
    c = 0.25    # - 0.25 of bad pages TFIDFs

    print("------------------------------------------------------------")
    #print(list(queries_df['TFIDF'][0].values()))
    good = []
    for i in better:
        worse.remove(int(i))
        #print(list(queries_df['TFIDF'][0].values()))
        good.append(list(queries_df['TFIDF'][int(i)].values()))

    bad = []
    for i in worse:
        bad.append(list(queries_df['TFIDF'][int(i)].values()))
    
    best_query = np.dot(a,list(full_query_vector.values()))
    with open('original_query.txt', 'w') as f:
        for item in best_query:
            f.write("%s\n" % item)

    for i in good:
        best_query = np.add(best_query,np.dot(b,i))
    for i in bad:
        best_query = np.subtract(best_query, np.dot(c, i))

    with open('optimized_query.txt', 'w') as f:
        for item in best_query:
            f.write("%s\n" % item)

    return best_query

def optimized_query(better, queries_df, full_query_vector, results):
    best_query = create_optimized_query(better, queries_df, full_query_vector)
    tfidf_list = results["TFIDF"].tolist()
    similarity_matrix = cosine_similarity1(best_query,tfidf_list)

    results['Score'] = np.array(similarity_matrix)
    results.sort_values(by=['Score'], inplace=True, ascending=False)
    #print(query_data[["Content","Score"]].head())
    #print(query_data)
    counter=0
    for i in full_query_vector.keys():
        full_query_vector[i] = best_query[counter]
        counter = counter + 1
    print(full_query_vector)
    return results, full_query_vector ##

    #return res2

def query_search(query):
    data = pd.read_csv("database.csv")
    data = preprocessing(data)
    globalDict, documentsTF = TF_Process(data)
    #print(documentsTF[0])
    dictionaryIDF = IDF_Process(globalDict,data.shape[0]) 
    #print(dictionaryIDF[0])
    query = query_Preprocessing(query)
    queryGlobalDict, queryTF = query_TF_Process(query,data,globalDict)
    queryDictionaryIDF = query_IDF_Process(query, queryGlobalDict, dictionaryIDF, data.shape[0])

    queryTFIDF={}
    for i in query:
        queryTFIDF[i] = queryDictionaryIDF[i]*queryTF[i]

    # if any of the queries terms doesn't exist in our database, then give them a value of zero
    for i in query:
        if not i in dictionaryIDF.keys():
            dictionaryIDF[i]=0
    # fill documentsTF's documents' missing key:value pairs with key=key:value=0
    for i in dictionaryIDF.keys():
        for j in range(len(documentsTF)):
            if not i in documentsTF[j]:
                documentsTF[j][i]=0

    tfidf_list = []
    for single_doc in documentsTF:
        tfidf_list.append(create_vector(single_doc, queryDictionaryIDF, queryGlobalDict))
    
    full_query_vector={}
    for term in queryGlobalDict.keys():
        full_query_vector[term] = 0
    
    for term in query:
        full_query_vector[term] = queryTFIDF[term]

    
    #similarity_matrix = cosine_similarity(query, queryTFIDF, documentsTF, dictionaryIDF)
    query_vector_list = list(full_query_vector.values())
    similarity_matrix = cosine_similarity1(query_vector_list,tfidf_list)
    query_data = data.copy()
    query_data['TFIDF'] = tfidf_list
    query_data['Score'] = np.array(similarity_matrix)
    query_data.sort_values(by=['Score'], inplace=True, ascending=False)
    #print(query_data[["Content","Score"]].head())
    #print(query_data)
    return query_data, full_query_vector

# if __name__ == "__main__":

#     data = pd.read_csv("database.csv")
#     preprocessing(data)
#     globalDict, documentsTF = TF_Process(data)
#     dictionaryIDF = IDF_Process(globalDict,data.shape[0]) 
#     query = "Coronavirus"
#     query = query_Preprocessing(query)
#     queryGlobalDict, queryTF = query_TF_Process(query,data,globalDict)
#     queryDictionaryIDF = query_IDF_Process(query, queryGlobalDict, data.shape[0])
#     queryTFIDF={}
#     for i in query:
#         queryTFIDF[i] = queryDictionaryIDF[i]*queryTF[i]

#     # if any of the queries terms doesn't exist in our database, then give them a value of zero
#     for i in query:
#         if not i in dictionaryIDF.keys():
#             dictionaryIDF[i]=0
#     # fill documentsTF's documents' missing key:value pairs with key=key:value=0
#     for i in dictionaryIDF.keys():
#         for j in range(len(documentsTF)):
#             if not i in documentsTF[j]:
#                 documentsTF[j][i]=0

#     similarity_matrix = cosine_similarity(query, queryTFIDF, documentsTF, dictionaryIDF)
#     query_data = data.copy()
#     query_data['Score'] = np.array(similarity_matrix)
#     query_data.sort_values(by=['Score'], inplace=True, ascending=False)
#     print(query_data[["Content","Score"]].head())

    