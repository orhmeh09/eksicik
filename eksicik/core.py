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
idDelimiter = "--"
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

class Baslik:
    def __init__(self, name = None, prettyName = None, id_=None, counter=None, wholePath=None):
        self.name = name
        self.prettyName = prettyName
        self.id_ = id_
        self.counter = counter
        self.entries = []
        self.numberOfPages = None
        self.numberOfEntries = None

        if wholePath:
            self.name = wholePath.rsplit('--',1)[0]
            self.id_ = wholePath.rsplit('--',1)[1]

        if not self.id_ and not self.name:
            raise Exception("Baslik does not have enough info for processing")

    def getJson(self):
        return json.dumps({'name': self.name,
                           'prettyName': self.prettyName,
                           'counter': self.counter,
                           'id': self.id_},
                          indent=4,
                          encoding="utf-8",
                          ensure_ascii=False,
                          sort_keys=False,
                          separators=(',', ': '))

    def getNumberOfPages(self):
        url = eksiUrl + self.getPath()
        firstPage = urllib2.urlopen(url)
        html = firstPage.read()

        # print html
        soup = BeautifulSoup(html)
        self.numberOfPages = int(soup.find('div', class_='pager')['data-pagecount'])
        return self.numberOfPages

    def getPath(self):
        return self.name + idDelimiter + str(self.id_)

    def getNumberOfEntriesAndPages(self):
        """Baslikta toplam kac adet entry oldugunu bul"""
        self.getNumberOfPages()
        lastPageUrl = eksiUrl + self.getPath() + "?p=" + str(self.numberOfPages)
        lastPage = urllib2.urlopen(lastPageUrl)
        html = lastPage.read()
        soup = BeautifulSoup(html)
        self.numberOfEntries = int(soup.find('ol', id='entry-list').find_all('li')[-1].attrs['value'])

        return self.numberOfEntries, self.numberOfPages

    def getNumberOfEntries(self):
        self.getNumberOfEntriesAndPages()
        return self.numberOfEntries

    def getFinalAralik(self, aralik=None, aralikIsForPages=False):
        global entryPerPage
        firstEntry = 1
        firstPage = 1
        lastPage = 1
        firstEntryCoordinateInPage = 1
        lastEntryCoordinateInPage = entryPerPage

        if not aralikIsForPages:
            self.getNumberOfEntriesAndPages() # 2 requests
            logging.info("Basliktaki toplam entry, toplam sayfa: "
                         + str(self.numberOfEntries)+", "+str(self.numberOfPages))
            if aralik:
                firstEntry = min(aralik[0], self.numberOfEntries)
                lastEntry = min(aralik[1], self.numberOfEntries)
            else:
                lastEntry = self.numberOfEntries
            logging.info("Indirilecek entry araligi: "+str(firstEntry)+"-"+str(lastEntry))

            firstPage,firstEntryCoordinateInPage,lastPage,lastEntryCoordinateInPage = calcPageAralikFromEntryAralik(firstEntry, lastEntry)
        else:
            self.getNumberOfPages() # 1 request
            logging.info("Basliktaki toplam entry, toplam sayfa: "+str(self.numberOfPages))
            if aralik:
                firstPage = aralik[0]
                lastPage = aralik[1]
                if firstPage > self.numberOfPages:
                    firstPage = self.numberOfPages
                    firstEntryCoordinateInPage = entryPerPage + 1
                # if lastPage > numberOfPages:
                #     lastPage = numberOfPages
                lastPage = min(aralik[1], self.numberOfPages)
            else:
                lastPage = self.numberOfPages

            lastEntryCoordinateInPage = entryPerPage
        return firstPage,firstEntryCoordinateInPage,lastPage,entryPerPage

    def getAllEntries(self, aralik=None, aralikIsForPages=False):
        """Basliktaki butun entryleri indir

        Arguments:
        aralik -- 2 ogeli int arrayi, ornek=[1,10]
        aralikIsForPages -- aralik entry araligi mi, yoksa sayfa araligi mi
        """
        self.entries = []
        logging.info("Getting all entries of: "+self.name)

        firstPage,firstEntryCoordinateInPage,lastPage,lastEntryCoordinateInPage = self.getFinalAralik(aralik=aralik, aralikIsForPages=aralikIsForPages)

        logging.info(str(firstPage)+" "+
                     str(firstEntryCoordinateInPage)+" "+
                     str(lastPage)+" "+str(entryPerPage))

        for n in range(firstPage, lastPage+1):
            if (firstPage-1)*entryPerPage + firstEntryCoordinateInPage > (lastPage-1)*entryPerPage + lastEntryCoordinateInPage:
                break
            logging.info(self.name+" -- sayfa: "+str(n)+"/"+str(lastPage))
            entries = self.getEntriesFromPage(n)
            if n == firstPage:
                self.entries += entries[firstEntryCoordinateInPage-1:]
            elif n == lastPage:
                self.entries += entries[:lastEntryCoordinateInPage]
            else:
                self.entries += entries
        return self.entries

    def getEntriesFromPage(self, sayfa):
        """Basliktan belli bir sayfayi cek

        Arguments:
        sayfa -- sayfa numarasi (1 den baslayan int)
        """
        url = eksiUrl + self.getPath()
        sayfaUrl = url + "?p=" + str(sayfa)
        result = getEntriesFromUrl(sayfaUrl)
        return result


class Liste:
    def __init__(self, name=None):
        self.name = name
        self.basliks = []
        self.numberOfPages = None

    def getNumberOfPages(self):
        url = eksiUrl + self.name
        firstPage = urllib2.urlopen(url)
        html = firstPage.read()

        # print html
        soup = BeautifulSoup(html)
        self.numberOfPages = int(soup.find('div', class_='pager')['data-pagecount'])
        return self.numberOfPages

    def getBasliksFromPage(self, sayfa):
        url = eksiUrl + self.name
        sayfaUrl = url + "?p=" + str(sayfa)
        result = getBasliksFromUrl(sayfaUrl)
        return result

    def getAllBasliks(self, aralik=None):
        """Listedeki butun basliklari indir

        Arguments:
        aralik -- 2 ogeli int arrayi, ornek=[1,10]
        """
        self.basliks = []
        self.getNumberOfPages()
        firstPage,lastPage = 1, self.numberOfPages
        if aralik:
            lastPage = min(aralik[1], self.numberOfPages)
            if firstPage > lastPage:
                firstPage = lastPage + 1

        for n in range(firstPage, lastPage+1):
            logging.info(self.name+" -- sayfa: "+str(n)+"/"+str(lastPage))
            if firstPage > lastPage:
                break
            basliks = self.getBasliksFromPage(n)
            # for i in basliks: print(i.name)
            self.basliks += basliks

        return self.basliks

    def getAllBaslikEntries(self):
        if self.basliks == []:
            self.getAllBasliks()
        for i in self.basliks:
            i.getAllEntries()

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


def getBasliksFromUrl(url):
    page = urllib2.urlopen(url)
    html = page.read()
    soup = BeautifulSoup(html)
    result = []

    for i in soup.find_all('ul', class_='topic-list')[-1].find_all('li'):
        path = i.find('a').attrs['href']
        # print("ASDASDASDASDASDASD\n"+str(i))
        # import pdb; pdb.set_trace();
        # print(i.find('a').attrs['class'])
        if i.find('a').attrs['class'][0] == "sponsored":
            continue

        name = path[1:].rsplit('?', 1)[0].rsplit('--',1)[0]
        id_ = path[1:].rsplit('?', 1)[0].rsplit('--',1)[1]
        counter = None
        if i.find('small'):
            counter = int(i.find('small').getText().encode('utf-8').strip())
            i.small.decompose()

        prettyName = i.string.encode('utf-8').strip()
        # path.rsplit('?', 1)
        # print(id_)
        result.append(Baslik(prettyName=prettyName, name=name, id_=id_, counter=counter))

    return result


def textWithNewlines(elem):
    text = ''
    for e in elem.recursiveChildGenerator():
        if isinstance(e, basestring):
            text += e.strip()
        elif e.name == 'br':
            text += '\n'
    return text
