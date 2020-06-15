import json
import alloimport
import os
import requests
import random
import allodb
import statistics
import math

FILE="selection.csv"
DIR="allocine"
def select(file):
    COUNT=1000

    x = allodb.DB("db/allodb.db")
    ret = x.exec("select id, name, nnote from films where id in (select id from films where name!='' and nnote>0 and year>2000 order by random() limit 1000) order by nnote asc;")

    print(len(ret))
    i=0
    with open(file, "w") as f:
        for x in ret:
            print("%d;%s" % (x[0], x[1]))
            f.write("%d;%s;\n" % (x[0], x[1]))
            i+=1
            if i>=COUNT: break



def jsonload(file):
    with open(file) as f:
        js=json.loads(f.read())
    return js



def _compare():
    db=allodb.DB("db/allodb.db")
    udb={}
    print("titre;nnoteA;nnoteB;line")
    for file in os.listdir("allocine"):
        if file.endswith(".json"):
            tmp=jsonload("allocine/%s" % file)
            udb[int(tmp[0])]=tmp
            film=db.get_film_by_id('fanch' , int(tmp[0])).row_at(0)
            print("%s;%d;%d;%f" % (tmp[1], film[12], tmp[12], calc_lin(film[12], tmp[12], 140*24*3600)))
    with open("user/obj.json", "w") as f:
        f.write(json.dumps(udb))

def dl(fid):
    url="http://www.allocine.fr/film/fichefilm_gen_cfilm=%d.html" % fid
    req = requests.get(url)
    with open(os.path.join(DIR, str(fid)+".html"), "wb") as f:
        f.write(req.content)
    with open(os.path.join(DIR, str(fid)+".json"), "w") as f:
        f.write(json.dumps(alloimport.extract(req.content.decode("utf-8"), allodb.DB.COLUMNS)))


def download(file):
    n=0
    with open(file) as f:
        for line in f.readlines():
            l=line.split(";")
            dl(int(l[0]))
            print(n/10)
            n+=1


results=[]
def calc_prio(a, b, raw, t):
    if not a: a=1
    if not b: b=1
    t/=3600 * 24*30 # par mois
    pc=(100*(b)/a) ** (1/t) # augmentation de note (en pourcentage/mois)

    r=min(pc,10)*10*min(math.log(b, 10),4) if pc else 0
    return r+(r*((raw[12]+1)/10))

def compare():
    _js = jsonload("user/obj.json")
    _old=jsonload("user/old.json")
    for key in _js:
        js=_js[key]
        old=_old[key]
        results.append((js[1], old[13],  js[13] ,calc_prio(old[13],  js[13], js, 140*3600*24)))

def printresults():
    global results
    results=sorted(results, key=lambda x: x[3])
    for x in results:
        tmp=("%s;%d;%d;%.2f" % x).replace(".", ",")
        print(tmp)

    tmp=results[0:]
    res=list(map(lambda x: (x[0], x[3], 100*((x[2]-x[1])/x[1])), tmp))
    print(res)
compare()
printresults()