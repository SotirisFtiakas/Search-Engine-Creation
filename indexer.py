import pandas as pd
import numpy as np
import string
import math

# Function for data preprocessing
def preprocessing(data):
    # Make all letters lowercase
    data["Content"] = data["Content"].str.lower()

    # Remove punctuation
    data["Content"] = data["Content"].str.translate(str.maketrans('', '', string.punctuation))

    # Remove stopwords
    f = open("stopwords.txt", "r")
    stopwords = f.read()

    for i, row in data.iterrows():
        data.at[i,'Content'] = ' '.join([word for word in data.at[i,'Content'].split() if word not in stopwords])
    
    return data
    

# Function to calculate the normalized TF of a word in a document
def termFrequency(term,all_words,sum_of_words):
    return all_words.count(term) / float(sum_of_words)


# Function to calculate TF for every term in every document
def TF_Process(data):
    globalDict = {}     # Global dictionary where:
                            # key = term
                            # value = documents where term can be found

    documentsTF = []    # List that will store dictionaries where:
                            # List index = document id
                                # key = term
                                # value = TF in the particular document

    for i, row in data.iterrows():
        content = data.at[i,'Content']
        
        # Take number of all non-unique words in a document
        all_words = content.split()
        sum_of_words = len(all_words)

        TF={}   # Dictionary where:
                    # key = term, 
                    # value = TF in the document 
        
        for term in all_words:
        
            # update global dictionary with all the documents where a term belongs
            if not term in globalDict:
                globalDict[term] = [i]
            elif not term in TF:
                doc_list = globalDict.get(term)
                doc_list.append(i)
                globalDict[term] = doc_list

            # calculate the TF    
            TF[term] = termFrequency(term,all_words,sum_of_words)
        
        documentsTF.append(TF)
        
    return globalDict, documentsTF


# Function to calculate IDF for every term
def IDF_Process(globalDict,total_docs):
    dictionaryIDF = globalDict.copy()
    for i in dictionaryIDF.keys():
        dictionaryIDF[i] = 1 + math.log(float(total_docs/len(dictionaryIDF[i])))
    return dictionaryIDF


if __name__ == "__main__":

    data = pd.read_csv("database.csv")
    preprocessing(data["Content"])
    globalDict, documentsTF = TF_Process(data)
    dictionaryIDF = IDF_Process(globalDict,data.shape[0]) 



