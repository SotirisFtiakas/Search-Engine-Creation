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
        downloaded = trafilatura.fetch_url(link.get('href'))
        if trafilatura.extract(downloaded) != None:
            temp.append(link.get('href'))
            my_dict[link.get('href')] = trafilatura.extract(downloaded)



def write_to_file(my_dict):
    df = pd.DataFrame(my_dict.items())
    df.to_csv(r'database.csv')      

if __name__ == "__main__":
    temp = []
    number_of_threads = 5
    base_url = "https://www.nytimes.com/"
    number_of_urls = 100

    my_dict = {}

    start = time.time()
    print(len(my_dict))
    getLinks(base_url, temp, my_dict)
    print(len(my_dict))

    if len(my_dict) < number_of_urls:
        for link in temp:
            getLinks(link, temp, my_dict)
            print(len(my_dict))
            if len(my_dict) > number_of_urls:
                break

    end = time.time()
    print("Total time of crawling: ", end - start, "seconds")
    write_to_file(my_dict)