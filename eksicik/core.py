from __future__ import division, print_function, absolute_import
from bs4 import BeautifulSoup
import argparse
import urllib2
import datetime

eksi_url = "https://eksisozluk.com/"

class Entry:
    def __init__(self, comment = None, author = None, number = None, datetime=None):
        self.comment = comment
        self.author = author
        self.number = number
        self.datetime = datetime
        # if not (self.datetime == None or isinstance(self.datetime, datetime.datetime)):
            # raise Exception("The date should be of type datetime.datetime")

    def __str__(self):
        result = "<entry"
        if self.datetime != None:
            result += " date=\""+ str(self.datetime) +"\""
        if self.author != None:
            result += " author=\""+ self.author +"\""
        result += ">"
        result += self.comment
        result += "</entry>"
        return result

def getNumberOfPagesOfBaslik(baslik):
    baslik_url = eksi_url + baslik
    firstpage = urllib2.urlopen(baslik_url)
    html = firstpage.read()

    # print html
    soup = BeautifulSoup(html)
    return int(soup.find('div', class_='pager')['data-pagecount'])

def getEntriesFromUrl(url):
    page = urllib2.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html)
    result = []
    for i in soup.find_all('article'):
        # import re
        # i = re.sub('<br\s*?>', '\n', i)
        comment = text_with_newlines(i.find('div', class_='content'))
        comment = comment.encode('utf-8').strip()
        author = i.find('span', itemprop='name').getText().encode('utf-8').strip()
        date = i.find('span',class_='entry-date').find('time',class_='creation-time').attrs['datetime']
        datetimeObject = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        # import pdb; pdb.set_trace()
        # comment = " ".join(i.find_all(text=lambda t: True)).encode('utf-8').strip()
        result.append(Entry(comment=comment, author=author, datetime=datetimeObject))
    return result

def text_with_newlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text

def getAllEntriesFromBaslik(baslik):
    result = []
    baslik_url = eksi_url + baslik
    numberOfPages = getNumberOfPagesOfBaslik(baslik)

    for n in range(numberOfPages):
        print(baslik+" -- page: "+str(n+1)+"/"+str(numberOfPages))
        page_url = baslik_url + "?p=" + str(n+1)
        result += getEntriesFromUrl(page_url)
    return result
