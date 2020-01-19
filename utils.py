import json
import os
import ast

import requests


def filter_nat(line):
    n=line.find('nationality"> ')
    if n>0:
        line=line[n+14:]
        nn=line.find("<")
        return line[:nn]
    return None

def filter_id(line):
    n=line.find('"movie_id":"')
    if n>0:
        line=line[n+12:]
        n=line.find('"')
        return int(line[:n])
    return None

def filter_date(line):
    n=line.find('/annee-')
    if n>0:
        line=line[n+7:]
        nn=line.find("/")
        return int(line[:nn])
    n=line.find("production_year=")
    if n>0:
        line=line[n+16:]
        return int(line[:line.find('"')])
    return None

def jsonfromfile(f):
    with open(f, "r") as f:
        return json.loads(f.read())
    return None


def obj_to_arr(js, columns):
    arr=[]
    for x in columns:
        if isinstance(x, str): x=(x, None, None)
        if len(x) == 1: x=(x[0], None, None)
        if len(x) == 2: x=(x[0], x[1], None)
        v=jsval(js, *x[:3])
        arr.append(v)
    return arr


def _jsvalarray(js, path, fct, default):
    out=[]
    i = 0
    while i < len(path):
        x = path[i]
        if x == "*":
            if not isinstance(js, (list, tuple)): js=[js]
            i += 1
            for y in js:
                out.append(_jsval(y, path[i:], fct, default))
        elif js and isinstance(js, object) and x in js:
            js = js[x]
        else:
            return default
        i += 1
    return out

def _jsvalcommon(js, path, fct, default):
    for x in path:
        if js and isinstance(js, object) and x in js:
            js=js[x]
        else: return default
    return js

def _jsval(js, path, fct, default):
    if "*" in path: return _jsvalarray(js, path, fct, default)
    return _jsvalcommon(js, path, fct, default)


def jsval(js, path, fct=None, default=None):
    if isinstance(path, str): path=path.split("/")
    out=_jsval(js, path, fct, default)
    if fct and out: out=fct(out)
    return out


def castarr(x):
    if not isinstance(x, list): return [x]
    return x

def floatvirg(x):
    return float(x.replace(",", "."))



def extract(htmlcont, columns):
    content = htmlcont
    n = content.find('<script type="application/ld+json">')
    js = {}
    if n >= 0:
        content = content[n + 36:].replace("\r", "").replace("\n", "").replace("\t", "")
        n = content.find('</script>')
        if n >= 0:
            content = content[:n]
            js = json.loads(content)

    js["pays"] = []
    js["annee"] = None
    for line in htmlcont.split("\n"):
        x = filter_nat(line)
        if x: js["pays"].append(x)
        x = filter_date(line)
        if x: js["annee"] = x
        x = filter_id(line)
        if x: js["id"] = x
    x=obj_to_arr(js, columns)
    return x

def test(start, end):
    for i in range(start, end):
        path="/home/fanch/allocine/allocine/"+str(i)+".html"
        if os.path.isfile(path):
            obj_to_arr(jsonfromfile(path),
                       [
                           ("id", None, None, "id"),
                           ("name", None, None, "name"),
                           ("image/url", None, None, "image"),
                           ("pays/*", castarr, None, "nationality"),
                           ("annee",  None, None, "year"),
                           ("genre/*", castarr, None, "genre"),
                           ("description",  None, None, "description"),
                           ("director/*/name", None, None, "director"),
                           ("actor/*/name", castarr, None, "actor"),
                           ("creator/*/name", castarr, None, "creator"),
                           ("musicBy/*/name", castarr, None, "musicBy"),
                           ("aggregateRating/ratingValue", floatvirg, None, "note"),
                           ("aggregateRating/ratingCount", int, None, "nnote"),
                           ("aggregateRating/reviewCount", int, None, "nreview")
                       ])
        else:
            raise Exception(path+" does not exists")


#test(2,20)
i=0
if False:
    for file in os.listdir("/home/fanch/allocine/allocine"):
        cont = ""
        with open("/home/fanch/allocine/allocine/"+file) as f:
            i+=1
            x=f.read()
            print("/home/fanch/allocine/allocine/"+file, i)
            if x and x[0]=='"':
                cont = ast.literal_eval(x)
            else: cont=x


        if x and x[0] == '"':
            with open("/home/fanch/allocine/allocine/"+file, "w") as f:
                try:
                    f.write(cont)
                except UnicodeEncodeError:
                    x=requests.get("http://www.allocine.fr/film/fichefilm_gen_cfilm="+file[:file.find(".")]+".html")
                    f.write(x.text)
                    print("----->", "/home/fanch/allocine/allocine/"+file)

