from __future__ import division, print_function, absolute_import
from bs4 import BeautifulSoup
import argparse
import urllib2
import datetime
import json
# import sys
import logging
import math

logging.basicConfig(level=logging.INFO)

eksiUrl = "https://eksisozluk.com/"
entryPerPage = 10

# outputXml = False
# /populer, /bugun
class Entry:
    def __init__(self, comment = None, baslik = None,
                 author = None, number = None,
                 datetime = None, id_ = None,
                 prettyBaslik = None):

        self.comment = comment
        self.author = author
        self.number = number
        self.datetime = datetime
        self.baslik = baslik
        self.prettyBaslik = prettyBaslik
        self.id_ = id_

        # if not (self.datetime == None or isinstance(self.datetime, datetime.datetime)):
            # raise Exception("The date should be of type datetime.datetime")
    def getXml(self):
        return "<deprecated for now>"
        # result = "<entry"
        # if self.baslik != None:
        #     result += " baslik=\""+ self.baslik +"\""
        # if self.prettyBaslik != None:
        #     result += " prettyBaslik=\""+ self.prettyBaslik +"\""
        # if self.author != None:
        #     result += " author=\""+ self.author +"\""
        # if self.datetime != None:
        #     result += " datetime=\""+ str(self.datetime) +"\""
        # result += ">"
        # result += self.comment
        # result += "</entry>"
        # return result

    def getJson(self):
        return json.dumps({'baslik': self.baslik,
                           'prettyBaslik': self.prettyBaslik,
                           'author': self.author,
                           'number': self.number,
                           'id': self.id_,
                           'datetime': str(self.datetime),
                           'comment': self.comment},
                          indent=4,
                          encoding="utf-8",
                          ensure_ascii=False,
                          sort_keys=False,
                          separators=(',', ': '))

def getNumberOfPagesOfBaslik(baslik):
    """Baslikta toplam kac adet sayfa oldugunu bul

    Arguments:
    baslik -- baslik tanimlayici string
    """
    baslik_url = eksiUrl + baslik
    firstPage = urllib2.urlopen(baslik_url)
    html = firstPage.read()

    # print html
    soup = BeautifulSoup(html)
    return int(soup.find('div', class_='pager')['data-pagecount'])

def getNumberOfEntriesAndPagesOfBaslik(baslik):
    """Baslikta toplam kac adet entry oldugunu bul

    Arguments:
    baslik -- baslik tanimlayici string
    """
    numberOfPages = getNumberOfPagesOfBaslik(baslik)
    lastPageUrl = eksiUrl + baslik + "?p=" + str(numberOfPages)
    lastPage = urllib2.urlopen(lastPageUrl)
    html = lastPage.read()
    soup = BeautifulSoup(html)
    result = int(soup.find('ol', id='entry-list').find_all('li')[-1].attrs['value'])
    return result, numberOfPages

def getNumberOfEntriesOfBaslik(baslik):
    a,b = getNumberOfEntriesAndPagesOfBaslik
    return a

def getEntriesFromUrl(url):
    """Verilen URL'den entryleri cek

    Arguments:
    url -- adi ustunde, string
    """
    page = urllib2.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html)
    result = []

    # import pdb; pdb.set_trace()

    baslik = soup.find('h1', id='title').attrs['data-slug']
    prettyBaslik = soup.find('h1', id='title').attrs['data-title'].encode('utf-8').strip()

    for j in soup.find('ol', id='entry-list').find_all('li'):
        # import re
        # i = re.sub('<br\s*?>', '\n', i)
        i = j.find('article')
        number = int(j.attrs['value'])
        id_ = str(i.find('footer').attrs['data-id'])
        comment = textWithNewlines(i.find('div', class_='content'))
        comment = comment.encode('utf-8').strip()
        author = i.find('span', itemprop='name').getText().encode('utf-8').strip()
        date = i.find('span',class_='entry-date').find('time',class_='creation-time').attrs['datetime']
        datetimeObject = datetime.datetime.strptime(date, '%Y-%m-%dT%H:%M:%S')
        # import pdb; pdb.set_trace()
        # comment = " ".join(i.find_all(text=lambda t: True)).encode('utf-8').strip()
        result.append(Entry(comment = comment,
                            author = author,
                            datetime = datetimeObject,
                            baslik = baslik,
                            number = number,
                            id_ = id_,
                            prettyBaslik = prettyBaslik))
    return result

def getEntriesFromBaslikPage(baslik, sayfa):
    """Basliktan belli bir sayfayi cek

    Arguments:
    baslik -- baslik tanimlayici string
    sayfa -- sayfa numarasi (1 den baslayan int)
    """
    baslikUrl = eksiUrl + baslik
    sayfaUrl = baslikUrl + "?p=" + str(sayfa)
    result = getEntriesFromUrl(sayfaUrl)
    # for i in result:
    #     i.baslik = baslik
    return result

def textWithNewlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text

def calcPageAralikFromEntryAralik(firstEntry, lastEntry):
    firstPage = int(math.floor(float(firstEntry) / float(entryPerPage) + 1))
    lastPage = int(math.floor(float(lastEntry) / float(entryPerPage) + 1))
    firstEntryCoordinateInPage = firstEntry % entryPerPage
    lastEntryCoordinateInPage = lastEntry % entryPerPage

    if lastEntryCoordinateInPage == 0:
        lastPage -= 1
        lastEntryCoordinateInPage = entryPerPage
    if firstEntryCoordinateInPage == 0:
        firstPage -= 1
        firstEntryCoordinateInPage = entryPerPage

    return firstPage, firstEntryCoordinateInPage, lastPage, lastEntryCoordinateInPage

def getFinalAralik(baslik, aralik=None, aralikIsForPages=False):
    global entryPerPage
    firstEntry = 1
    firstPage = 1
    lastPage = 1
    firstEntryCoordinateInPage = 1
    lastEntryCoordinateInPage = entryPerPage

    logging.info("Basliktaki toplam entry, toplam sayfa: " + str(getNumberOfEntriesAndPagesOfBaslik(baslik)))

    if not aralikIsForPages:
        numberOfEntries, numberOfPages = getNumberOfEntriesAndPagesOfBaslik(baslik) # 2 request
        if aralik:
            firstEntry = min(aralik[0], numberOfEntries)
            lastEntry = min(aralik[1], numberOfEntries)
        else:
            lastEntry = numberOfEntries
        logging.info("Indirilecek entry araligi: "+str(firstEntry)+"-"+str(lastEntry))

        firstPage,firstEntryCoordinateInPage,lastPage,lastEntryCoordinateInPage = calcPageAralikFromEntryAralik(firstEntry, lastEntry)
    else:
        numberOfPages = getNumberOfPagesOfBaslik(baslik) # 1 request
        if aralik:
            firstPage = aralik[0]
            lastPage = aralik[1]
            if firstPage > numberOfPages:
                firstPage = numberOfPages
                firstEntryCoordinateInPage = entryPerPage + 1
            # if lastPage > numberOfPages:
            #     lastPage = numberOfPages
            lastPage = min(aralik[1], numberOfPages)
        else:
            lastPage = numberOfPages

        lastEntryCoordinateInPage = entryPerPage
    return firstPage,firstEntryCoordinateInPage,lastPage,entryPerPage


def getAllEntriesFromBaslik(baslik, aralik=None, aralikIsForPages=False):
    """Basliktaki butun entryleri indir

    Arguments:
    baslik -- baslik tanimlayici string
    aralik -- 2 ogeli int arrayi, ornek=[1,10]
    """
    result = []

    firstPage,firstEntryCoordinateInPage,lastPage,lastEntryCoordinateInPage = getFinalAralik(baslik, aralik=aralik, aralikIsForPages=aralikIsForPages)

    logging.info(str(firstPage)+" "+
                 str(firstEntryCoordinateInPage)+" "+
                 str(lastPage)+" "+str(entryPerPage))

    for n in range(firstPage, lastPage+1):
        if (firstPage-1)*entryPerPage + firstEntryCoordinateInPage > (lastPage-1)*entryPerPage + lastEntryCoordinateInPage:
            break
        logging.info(baslik+" -- sayfa: "+str(n)+"/"+str(lastPage))
        entries = getEntriesFromBaslikPage(baslik, n)
        if n == firstPage:
            result += entries[firstEntryCoordinateInPage-1:]
        elif n == lastPage:
            result += entries[:lastEntryCoordinateInPage]
        else:
            result += entries
    return result
