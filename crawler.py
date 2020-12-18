from bs4 import BeautifulSoup
import requests
import re
import time
import trafilatura
import threading
import numpy as np

from flask import Flask
from flask_mysqldb import MySQL
import yaml

crawler = Flask(__name__)

# Configure db
db = yaml.safe_load(open('db.yaml'))
crawler.config['MYSQL_HOST'] = db['mysql_host']
crawler.config['MYSQL_USER'] = db['mysql_user']
crawler.config['MYSQL_PASSWORD'] = db['mysql_password']
crawler.config['MYSQL_DB'] = db['mysql_db']

mysql = MySQL(crawler)

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

def write_to_database(temp):
    for url in temp:
        with crawler.app_context():
            cur = mysql.connection.cursor()
            #content = trafilatura.fetch_url(url)
            cur.execute("INSERT INTO urls(url) VALUES(%s)", (url,))
            mysql.connection.commit()
            cur.close()

if __name__ == "__main__":
    temp = []
    number_of_threads = 5
    base_url = "https://www.nytimes.com/"
    number_of_urls = 100

    getLinks(base_url, temp)
    print(len(temp))

    if len(temp) < number_of_urls:
        for link in temp:
            getLinks(link, temp)
            print(len(temp))
            if len(temp) > number_of_urls:
                break

    write_to_file(temp)
    write_to_database(temp)