# Importing needed libraries
from flask import Flask

from bs4 import BeautifulSoup
import trafilatura

import requests
import re

import threading
import numpy as np
import pandas as pd
import time

crawler = Flask(__name__)

def getLinks(url, temp, my_dict):
    """
    Get the html content of the base url (page) and finds all available links.
    Then creates threads in order to make the payload shorter

    Parameters:
    url (String): The base url.
    temp (List): empty list that will be filled with links.
    my_dict (Dict): Dictionary that will be used to fill database.

    Returns:
    Void function

    """
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
    """
    The scrapping function that will iterate through all the list of given urls.

    Parameters:
    url_list (List): List of urls.

    Returns:
    Void function

    """
    for link in url_list:
        url = link.get('href')
        downloaded = trafilatura.fetch_url(url)

        # Checking the content of page.
        if trafilatura.extract(downloaded) != None:

            # Make a GET request to fetch the raw HTML content
            html_content = requests.get(url).text

            # Parse the html content
            soup = BeautifulSoup(html_content, "lxml")

            temp.append(url)
            
            # Complete the dictionary.
            my_dict['Url'].append(url)
            my_dict['Title'].append(soup.title.text)
            my_dict['Content'].append(trafilatura.extract(downloaded))
            my_dict['Score'].append(0) # all scores are initialized at 0.


def write_to_file(my_dict):
    """
    Create the CSV file of the database from a dictionary.

    Parameters:
    my_dict (Dict): List of urls.

    Returns:
    Void function

    """
    df = pd.DataFrame.from_dict(my_dict, orient='index')
    transpose_df = df.T
    transpose_df.to_csv(r'database.csv')      

if __name__ == "__main__":
    temp = []
    number_of_threads = 5 # The preferable number of threads.
    base_url = "https://www.nytimes.com/" # The base url-link, from which the program will start crawling and scrapping.
    number_of_urls = 100 # The preferable number of different urls-links.

    # Dictionary with lists for urls, titles, content and score.
    my_dict = {'Url':[], 'Title':[], 'Content':[], 'Score':[]}

    start = time.time()
    print(len(temp))
    getLinks(base_url, temp, my_dict)
    print(len(temp))

    # Checking the number of urls we have collected.
    if len(temp) < number_of_urls:
        for link in temp:
            getLinks(link, temp, my_dict)
            print(len(temp))
            if len(temp) > number_of_urls:
                break

    end = time.time()
    print("Total time of crawling: ", end - start, "seconds")
    write_to_file(my_dict)