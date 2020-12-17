from bs4 import BeautifulSoup
import requests
import re
import time
import trafilatura
import threading
import numpy as np

def getLinks(url, temp):
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


def write_to_file(temp):
    with open('urls.txt', 'w', encoding="utf-8") as f:
        for link in temp:
            f.write("%s\n" % link)

if __name__ == "__main__":
    temp = []
    number_of_threads = 5
    base_url = "https://www.nytimes.com/"
    number_of_urls = 200

    getLinks(base_url, temp)
    print(len(temp))

    if len(temp) < number_of_urls:
        for link in temp:
            getLinks(link, temp)
            print(len(temp))
            if len(temp) > number_of_urls:
                break

    write_to_file(temp)