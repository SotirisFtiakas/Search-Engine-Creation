from bs4 import BeautifulSoup
import requests
import re
import time

temp = []

def getLinks(url):
    try:
        r = requests.get(url, timeout=2)
        if (r.status_code == 200):
            html_page = r.text
            soup = BeautifulSoup(html_page, features="lxml")

            for link in soup.findAll('a', attrs={'href': re.compile("^https://")}):
                temp.append(link.get('href'))
    except requests.exceptions.RequestException:
        print("Skip this one!")


getLinks("https://www.nytimes.com/")
print(len(temp))

for link in temp:
    getLinks(link)
    print(len(temp))
    if len(temp) > 200:
        break

with open('urls.txt', 'w', encoding="utf-8") as f:
    for link in temp:
        f.write("%s\n" % link)