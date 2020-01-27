import json
import os
import re
import time

import requests

def filter_nat(line):
    n=line.find('nationality"> ')
    if n>0:
        line=line[n+14:]
        nn=line.find("<")
        return line[:nn]
    return None


def filter_date(line):
    n=line.find('/annee-')
    if n>0:
        line=line[n+7:]
        nn=line.find("/")
        return int(line[:nn])
    return None



def allofilter(content, id):
    old=content
    n = content.find('<script type="application/ld+json">')
    js=None
    if n >= 0:
        content = content[n + 36:].replace("\r", "").replace("\n", "").replace("\t", "")
        n = content.find('</script>')
        if n >= 0:
            content = content[:n]
            js=json.loads(content)
            if js:
                js["pays"] = []
                js["annee"] = None
                for line in old.split("\n"):
                    x = filter_nat(line)
                    if x: js["pays"].append(x)
                    x = filter_date(line)
                    if x: js["annee"] = x

    return js

def allofilterreq(id):
    url='http://www.allocine.fr/film/fichefilm_gen_cfilm='+str(id)+'.html'
    req=None
    while req==None:
        try:
            req=requests.get(url)
        except:
            req=None
            time.sleep(5)
    if req.status_code==200:
        return allofilter(req.text, id)
    print("Error "+str(req.status_code)+" for "+str(id))
    return None


def allofilterfile(file):
    content=""
    with open(file, "r") as f:
        content=f.read()
    return allofilter(content, file)


def allosniffer(dir, fr, to):
    for i in range(fr, to):
        js = allofilterreq(i)
        if js:
            with open(os.path.join(dir, str(i)+".json"), "w") as f:
                js["id"]=i
                f.write(json.dumps(js))
                #print(json.dumps(js))


def allofilterdir(dir : str, outdir : str):
    for file in os.listdir(dir):
        if file.endswith(".html"):
            n=int(file[file.find("=")+1:file.rfind(".")])
            js=allofilter(os.path.join(dir,file))
            if js:
                with open(os.path.join(outdir, str(n)+".json"), "w") as f:
                    js["id"]=n
                    f.write(json.dumps(js))
                    print("OK " + str(n))
            else:
                print("FAIL "+str(n))


#print(allofilter("/home/fanch/tmp/fichefilm_gen_cfilm=921.html"))
#allofilterdir("/home/fanch/tmp/", "/home/fanch/Documents/allocine")

#allosniffer("/home/fanch/allocine", 22538, 280000)
allosniffer("/home/fanch/allocine", 1, 100)