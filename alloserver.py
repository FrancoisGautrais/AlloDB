import json
import os
import time
import uuid
from urllib.parse import unquote_plus
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
    if x["match"]!=None: l.append('"'+unquote_plus(x["match"])+'" in name ')

    # 2/3 pays
    if x["pays"]!=None and x["pays-op"]!=None:
        tmp="("
        arr=x["pays"]
        for i in range(len(arr)):
            tmp+=(x["pays-op"] if i>0 else "")+' "'+unquote_plus(arr[i])+'" in nationality '
        l.append(tmp+")")
    #4/5 genre
    if x["genre"] != None and x["genre-op"] != None:
        tmp = "("
        arr = x["genre"]
        for i in range(len(arr)):
            tmp += (x["genre-op"] if i > 0 else "") + ' "' + unquote_plus(arr[i]) + '" in genre '
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
    if x["actor"]!=None: l.append('"'+unquote_plus(x["actor"])+'" in actor ')

    #18
    if x["director"]!=None: l.append('"'+unquote_plus(x["director"])+'" in director ')

    #19
    if x["tosee"]!=None: l.append(' tosee '+("=" if x["tosee"] else "!=") + " True")

    #20
    if x["seen"]!=None: l.append(' seen '+("=" if x["seen"] else "!=") + " True")

    base = "select * where ("
    for i in range(len(l)):
        base+=("and" if i>0 else "")+l[i]
    if len(l)==0: base+="True"
    base+=") "



    if x["order"]!=None and x["order-sort"]!=None:
        base+=" order by "+ x["order"]+" "
        if x["order-sort"]=="desc": base+="desc "

    if x["rand"]!=None and x["rand"]>0:
        base="rand("+base+", "+str(x["rand"])+" ) "


    log.info("Request = ", base)
    return base

class Request:
    def __init__(self, result):
        self.id=result.id
        self.result=result
        self.time=time.time()


class AlloServer(RESTServer):
    RESULT_PER_PAGE=10
    def __init__(self, user):
        RESTServer.__init__(self)
        self.requests={}
        self.user = user
        self.db = DB.fromjson("db.json", self.user)
        self.route("GET", "/", lambda req, res: res.serve_file_gen(config.www("index.html")))
        self.route("GET", "/index.html", lambda req, res: res.serve_file_gen(config.www("index.html")))
        self.route("GET", "/request", lambda req, res: res.serve_file_gen(config.www("request.html")))
        self.route("GET", "/import", lambda req, res: res.serve_file_gen(config.www("import.html")))
        self.route("POST", "/import", self.handle_import)
        self.route("GET", "/export", lambda req, res: res.serve_file(config.user("fanch"),  forceDownload=True))
        self.route("GET", "/director/#id", self.handle_director)
        self.route("GET", "/actor/#id", self.handle_actor)
        self.route("GET", "/film/#id", self.handle_film)
        self.route("POST", "/film/#id", self.handle_film_modify)
        self.route("GET", "/results/#id/#page", self.handle_results)
        self.route("POST", "/results", self.handle_results)
        self.static("/", config.WWW_DIR)

    def _check_query(self, req, query):
        if "type" in req.query:
            type=req.query["type"]
            order=req.query["order"] if "order" in req.query else ""
            query.sort(type, order!="desc")

    def handle_director(self, req: HTTPRequest, res: HTTPResponse):
        id=req.params["id"].replace("+", " ")
        if not id in self.db.directors: return res.serve404()
        path = config.www("results.html")
        tmp = Request(self.db.row_from_director(id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache())

    def handle_import(self, req: HTTPRequest, res: HTTPResponse):
        f=req.multipart_next_file()
        #f.save(config.user("fanch"), forcePath=True)
        x=f.parse_content()
        js=json.loads(x)
        self.db.userdata.import_json(js["db"])
        res.serve301("/")

    def handle_actor(self, req: HTTPRequest, res: HTTPResponse):
        id=req.params["id"].replace("+", " ")
        if not id in self.db.actors: return res.serve404()
        path = config.www("results.html")
        tmp = Request(self.db.row_from_actor(id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache())


    def handle_film(self, req: HTTPRequest, res: HTTPResponse):
        id=int(req.params["id"])
        if not id in self.db.ids: return res.serve404()
        path = config.www("film.html")
        tmp = Request(self.db.row_from_id(id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache())

    def handle_film_modify(self, req: HTTPRequest, res: HTTPResponse):
        id=int(req.params["id"])
        if not id in self.db.ids: return res.serve404()
        js = req.body_json()
        if not js: return res.serve400()

        row = self.db.ids[id]
        out=[]
        for x in js:
            out.append((x, js[x]))

        row.set(out)


    def handle_results(self, req : HTTPRequest, res : HTTPResponse):
        path = config.www("results.html")
        request = ""
        if req.method=="POST":
            body=req.body_json()
            if "json" in body:
                request=json_to_request(json.loads(body["json"]))
            elif "text" in body:
                request="(select * where "+unquote_plus(body["text"])+" )"
            tmp=Request(self.db.execute(request))
            x=tmp.result
            x.pagesize = AlloServer.RESULT_PER_PAGE
            self.requests[x.id]=tmp
        else:
            if "id" in req.params and "page" in req.params and req.params["id"] in self.requests:
                x=self.requests[req.params["id"]].result
                x.page=int(req.params["page"])-1
            else:
                return res.serve400()

        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache())

filecache.init()
usr = None
try :
    usr = user.User.fromjsonfile("fanch")
except:
    usr= user.User.createuser("fanch")


als = AlloServer(usr)
als.listen(8080)