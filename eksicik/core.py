from __future__ import division, print_function, absolute_import
from bs4 import BeautifulSoup
import argparse
import urllib2
import datetime
import json

eksi_url = "https://eksisozluk.com/"
# outputXml = False

class Entry:
    def __init__(self, comment = None, baslik = None, author = None, number = None, datetime=None):
        self.comment = comment
        self.author = author
        self.number = number
        self.datetime = datetime
        self.baslik = baslik

        # if not (self.datetime == None or isinstance(self.datetime, datetime.datetime)):
            # raise Exception("The date should be of type datetime.datetime")
    def getXml(self):
        result = "<entry"
        if self.baslik != None:
            result += " baslik=\""+ self.baslik +"\""
        if self.author != None:
            result += " author=\""+ self.author +"\""
        if self.datetime != None:
            result += " datetime=\""+ str(self.datetime) +"\""
        result += ">"
        result += self.comment
        result += "</entry>"
        return result

    def getJson(self):
        return json.dumps({'baslik': self.baslik,
                           'author': self.author,
                           'datetime': str(self.datetime),
                           'comment': self.comment},
                          sort_keys=True,
                          indent=4,
                          encoding="utf-8",
                          ensure_ascii=False,
                          separators=(',', ': '))

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

def getEntriesFromBaslikPage(baslik, page):
    baslikUrl = eksi_url + baslik
    pageUrl = baslikUrl + "?p=" + str(page)
    result = getEntriesFromUrl(pageUrl)
    for i in result:
        i.baslik = baslik
    return result

def text_with_newlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text

def getAllEntriesFromBaslik(baslik, sayfaAraligi=None):
    result = []
    firstPage = 0
    numberOfPages = getNumberOfPagesOfBaslik(baslik)

    if sayfaAraligi:
        firstPage = min(sayfaAraligi[0]-1, numberOfPages)
        lastPage = min(sayfaAraligi[1], numberOfPages)
    else:
        lastPage = numberOfPages

    for n in range(firstPage, lastPage):
        print(baslik+" -- sayfa: "+str(n+1)+"/"+str(lastPage))
        result += getEntriesFromBaslikPage(baslik, n+1)
    return result
