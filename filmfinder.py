import requests
from lxml import etree
import numpy as np

import log
import utils


def xrange(*x):

    return iter(range(*x))


def levenshtein(seq1, seq2):
    size_x = len(seq1) + 1
    size_y = len(seq2) + 1
    matrix = np.zeros ((size_x, size_y))
    for x in xrange(size_x):
        matrix [x, 0] = x
    for y in xrange(size_y):
        matrix [0, y] = y

    for x in xrange(1, size_x):
        for y in xrange(1, size_y):
            if seq1[x-1] == seq2[y-1]:
                matrix [x,y] = min(
                    matrix[x-1, y] + 1,
                    matrix[x-1, y-1],
                    matrix[x, y-1] + 1
                )
            else:
                matrix [x,y] = min(
                    matrix[x-1,y] + 1,
                    matrix[x-1,y-1] + 1,
                    matrix[x,y-1] + 1
                )
    return (matrix[size_x - 1, size_y - 1])

class Film:

    def __init__(self, site):
        self.site=site
        self.title=None
        self.year=None
        self.url=None
        self.langue=None



    def json(self):
        return {
            "site" : self.site,
            "title" : self.title,
            "year" : self.year,
            "langue" : self.langue,
            "url" : self.url
        }

class FilmFinder:
    def __init__(self, title, year=None):
        self.title=title
        self.year=year

    def find(self):
        x=self.do_find()
        out=[]

        for f in x:
            add = True
            if f.title.lower()!=self.title.lower(): add=False
            if self.year:
                dy = self.year - f.year if self.year > f.year else f.year - self.year
                if dy > 1: add = False
            if add:
                out.append(f.json())

        if len(out)>0: return out

        for f in x:
            add = True
            if levenshtein(f.title.lower(), self.title.lower()) >= 4: add = False
            if self.year:
                dy = self.year - f.year if self.year > f.year else f.year - self.year
                if dy > 1: add = False
            if add:
                out.append(f.json())
        return out


class ZoneTelechargementFinder(FilmFinder):
    HEAD = {
        "Host": "www.zone-telechargement2.vip",
        "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
        "Content-Type": "application/x-www-form-urlencoded",
        "Origin": "https://www.zone-telechargement2.vip",
        "DNT": "1",
        "Connection": "keep-alive",
        "Referer": "https://www.zone-telechargement2.vip/",
    }
    def do_find(self):
        req = requests.post("http://www.zone-telechargement2.vip/index.php?do=search", "do=search&subaction=search&search_start=0&full_search=1&result_from=1&story="+utils.urlencode(self.title)+"&titleonly=0&searchuser=&replyless=0&replylimit=0&searchdate=0&beforeafter=after&sortby=date&resorder=desc&showposts=1&catlist%5B%5D=2&user_hash=636b4560bb73a51b506836d8293f5770506a68d0", headers=ZoneTelechargementFinder.HEAD)
        dom = etree.HTML(req.content)
        out=[]
        for elem in (dom.xpath('//div[@class="mov"]')):
            try:
                f=Film("www.zone-telechargement2.vip")
                f.year=int(elem.findall('.//div[@class="mov-m"]/a')[0].text)
                f.langue=elem.findall('.//span[@class="langue"]/b')[0].text.strip()
                f.title=elem.findall('a[@class="mov-t nowrap"]')[0].get("title")
                f.url=elem.findall('a[@class="mov-t nowrap"]')[0].get("href")
                out.append(f)
            except: pass


        return out

class LiberttVfFinder(FilmFinder):
    HEAD={
            "Host" : "libertyvf.tv",
            "User-Agent" : "Mozilla/5.0 (X11; Linux x86_64; rv:71.0) Gecko/20100101 Firefox/71.0",
            "Accept" : "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language" : "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Content-Type" : "application/x-www-form-urlencoded",
            "Origin" : "https://libertyvf.tv",
            "Connection" : "keep-alive",
            "Referer" : "https://libertyvf.tv/",
            "Upgrade-Insecure-Requests" : "1",
            "Pragma" : "no-cache",
            "Cache-Control" : "no-cache",
            "TE" : "Trailers"
        }
    def do_find(self):
        req = requests.post("https://libertyvf.tv/v2/recherche/", "categorie=films&mot_search="+utils.urlencode(self.title), headers=LiberttVfFinder.HEAD)
        dom = etree.HTML(req.content)
        out=[]
        for elem in (dom.xpath('//div[@class="bloc-generale"]')):
            if elem.findall('h2'):
                f=Film("libertyvf.tv")
                f.title=elem.findall('h2/a')[0].text[13:]
                f.url=elem.findall('h2/a')[0].get("href")
                f.year=int(elem.xpath(".//a[contains(@href, 'https://libertyvf.tv/films/annee/')]")[0].text[8:])
                out.append(f)
        return out


FINDERS=[LiberttVfFinder, ZoneTelechargementFinder]

def find_film(title, year=None):
    out=[]
    for constr in FINDERS:
        x=constr(title, year)
        out+=x.find()
    return out

