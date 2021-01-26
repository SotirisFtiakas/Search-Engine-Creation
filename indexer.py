import pandas as pd
import numpy as np
import string

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
    

if __name__ == "__main__":

    data = pd.read_csv("database.csv")
    preprocessing(data)
    print(data["Content"])

