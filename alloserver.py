import json
import os

import config
from allodb import DB
import user
from http_server.restserver import RESTServer, HTTPRequest, HTTPResponse
from http_server import log, utils
from http_server.filecache import  filecache


def default(js, key, fct=None, default=None):
    x=js[key]
    if x=="": js[key]=None
    elif fct: js[key]=fct(x)


def json_to_request(x):
    l=[]
    # 1 match
    if x["match"]!=None: l.append('"'+x["match"]+'" in name ')

    # 2/3 pays
    if x["pays"]!=None and x["pays-op"]!=None:
        tmp="("
        arr=x["pays"]
        for i in range(len(arr)):
            tmp+=(x["pays-op"] if i>0 else "")+' "'+arr[i]+'" in nationality '
        l.append(tmp+")")
    #4/5 genre
    if x["genre"] != None and x["genre-op"] != None:
        tmp = "("
        arr = x["genre"]
        for i in range(len(arr)):
            tmp += (x["genre-op"] if i > 0 else "") + ' "' + arr[i] + '" in genre '
        l.append(tmp + ")")

    # 6 / 7 annee
    if x["year-min"]!=None and x["year-max"]!=None: l.append(' annee in range('+str(x["year-min"])+','+str(x["year-max"])+') ')
    elif x["year-min"]!=None: l.append(' year >= '+str(x["year-min"])+" ")
    elif x["year-max"]!=None: l.append(' year <= '+str(x["year-max"])+" ")


    # 8 / 9 note
    if x["note-min"]!=None and x["note-max"]!=None: l.append(' note in range('+str(x["note-min"])+','+str(x["note-max"])+') ')
    elif x["note-min"]!=None: l.append(' note >= '+str(x["note-min"])+" ")
    elif x["note-max"]!=None: l.append(' note <= '+str(x["note-max"])+" ")

    # 10 / 11 nnote
    if x["nnote-min"]!=None and x["nnote-max"]!=None: l.append(' nnote in range('+str(x["nnote-min"])+','+str(x["nnote-max"])+') ')
    elif x["nnote-min"]!=None: l.append(' nnote >= '+str(x["nnote-min"])+" ")
    elif x["nnote-max"]!=None: l.append(' nnote <= '+str(x["nnote-max"])+" ")

    # 12 / 13 nreview
    if x["nreview-min"]!=None and x["nreview-max"]!=None: l.append(' nreview in range('+str(x["nreview-min"])+','+str(x["nreview-max"])+') ')
    elif x["nreview-min"]!=None: l.append(' nreview >= '+str(x["nreview-min"])+" ")
    elif x["nreview-max"]!=None: l.append(' nreview <= '+str(x["nreview-max"])+" ")

    # 15 / 16 duration
    if x["duration-min"]!=None and x["duration-max"]!=None: l.append(' duration in range('+str(x["duration-min"])+','+str(x["duration-max"])+') ')
    elif x["duration-min"]!=None: l.append(' duration >= '+str(x["duration-min"])+" ")
    elif x["duration-max"]!=None: l.append(' duration <= '+str(x["duration-max"])+" ")

    #17
    if x["actor"]!=None: l.append('"'+x["actor"]+'" in actor ')

    #18
    if x["director"]!=None: l.append('"'+x["director"]+'" in director ')


    #19
    if x["tosee"]!=None: l.append(' tosee '+("=" if x["tosee"] else "!=") + " True")

    #20
    if x["seen"]!=None: l.append(' seen '+("=" if x["seen"] else "!=") + " True")

    base = "select * where ("
    for i in range(len(l)):
        base+=("and" if i>0 else "")+l[i]

    base+=") "
    if x["order"]!=None and x["order-sort"]!=None:
        base+=" order by "+ x["order"]+" "
        if x["order-sort"]=="desc": base+="desc "

    if x["rand"]!=None and x["rand"]>0:
        base="rand("+base+", "+str(x["rand"])+" ) "

    return base

class AlloServer(RESTServer):

    def __init__(self):
        RESTServer.__init__(self)
        self.user = user.User.createuser("Test")
        self.db = DB.fromjson("db.json", self.user)
        self.route("POST", "/results", self.handle_results)
        self.static_gen("/", config.WWW_DIR)

    def handle_results(self, req : HTTPRequest, res : HTTPResponse):
        path = config.www("results.html")
        request=json.loads(req.body_json()["request"])


        print(json_to_request(request))
        x=str(self.db.execute(json_to_request(request)))
        res.serve_file_gen(path, { "requests" : x})




filecache.init()

als = AlloServer()
als.listen(8080)