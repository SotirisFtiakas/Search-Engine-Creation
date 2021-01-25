from bs4 import BeautifulSoup
import requests
import re
import time
import trafilatura
import threading
import numpy as np
import pandas as pd
import time
import warnings #needed for this type of classifier
warnings.simplefilter(action='ignore', category=Warning)

from flask import Flask

crawler = Flask(__name__)

def getLinks(url, temp, my_dict):
    try:
        r = requests.get(url, timeout=2)
        if (r.status_code == 200):
            html_page = r.text
            soup = BeautifulSoup(html_page, features="lxml")
            
            all_urls = np.array_split(soup.findAll('a', attrs={'href': re.compile("^https://")}), number_of_threads)

            threads = list()
            for index in range(number_of_threads):
                x = threading.Thread(target=multi_threading_scrapping, args=(all_urls[index],))
                threads.append(x)
                x.start()
            
            for index, thread in enumerate(threads):
                thread.join()         
    except requests.exceptions.RequestException:
        print("Skip this one!")

def multi_threading_scrapping(url_list):
    for link in url_list:
        url = link.get('href')
        downloaded = trafilatura.fetch_url(url)
        if trafilatura.extract(downloaded) != None:
            # Make a GET request to fetch the raw HTML content
            html_content = requests.get(url).text
            # Parse the html content
            soup = BeautifulSoup(html_content, "lxml")

            temp.append(url)
            #print("hello there: ", soup.title.text)
            my_dict['Url'].append(url)
            my_dict['Title'].append(soup.title.text)
            my_dict['Content'].append(trafilatura.extract(downloaded))
            my_dict['Score'].append(0)


def write_to_file(my_dict):
    df = pd.DataFrame.from_dict(my_dict, orient='index')
    transpose_df = df.T
    transpose_df.to_csv(r'database.csv')      

if __name__ == "__main__":
    temp = []
    number_of_threads = 5
    base_url = "https://www.nytimes.com/"
    number_of_urls = 100

    my_dict = {'Url':[], 'Title':[], 'Content':[], 'Score':[]}

    start = time.time()
    print(len(temp))
    getLinks(base_url, temp, my_dict)
    print(len(temp))

    if len(temp) < number_of_urls:
        for link in temp:
            getLinks(link, temp, my_dict)
            print(len(temp))
            if len(temp) > number_of_urls:
                break

    end = time.time()
    print("Total time of crawling: ", end - start, "seconds")
    write_to_file(my_dict)