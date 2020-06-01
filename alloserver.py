import json
import os
import time
import sys

import requests

import filmfinder
from allolist import AlloList
import uuid
from urllib.parse import unquote_plus
import config
from allodb import DB
import user
from http_server.httpserver import HTTPServer
from http_server.log import Log
from http_server.restserver import RESTServer, HTTPRequest, HTTPResponse
from http_server import log, utils
from http_server.filecache import  filecache
from utils import dictassign, dictcopy, new_key
import utils

def default(js, key, fct=None, default=None):
    x=js[key]
    if x=="": js[key]=None
    elif fct: js[key]=fct(x)


def json_to_request(x):
    l=[]
    # 1 match
    if "match" in x and x["match"]!=None: l.append(' name like "%%'+unquote_plus(x["match"])+'%%" ')

    # 2/3 pays
    if "pays" in x and "pays-op" in x and x["pays"]!=None and x["pays-op"]!=None:
        tmp="("
        arr=x["pays"]
        for i in range(len(arr)):
            tmp+=(x["pays-op"] if i>0 else "")+' "'+unquote_plus(arr[i])+'" in nationality '
        l.append(tmp+")")
    #4/5 genre
    if "genre" in x and "genre-op" in x and x["genre"] != None and x["genre-op"] != None:
        tmp = "("
        arr = x["genre"]
        for i in range(len(arr)):
            tmp += (x["genre-op"] if i > 0 else "") + ' genre like "%%' + unquote_plus(arr[i]) + '%%"  '
        l.append(tmp + ")")

    if "userlist" in x and "userlist-op" in x and x["userlist"] != None and x["userlist-op"] != None:
        tmp = "("
        arr = x["userlist"]
        for i in range(len(arr)):
            tmp += (x["userlist-op"] if i > 0 else "") + ' lists like "%%' + unquote_plus(arr[i]) + '%%" '
        l.append(tmp + ")")

    # 6 / 7 annee
    if "year-min" in x and "year-max" in x and x["year-min"]!=None and x["year-max"]!=None: l.append(' annee in range('+str(x["year-min"])+','+str(x["year-max"])+') ')
    elif "year-min" in x and x["year-min"]!=None: l.append(' year >= '+str(x["year-min"])+" ")
    elif "year-max" in x and x["year-max"]!=None: l.append(' year <= '+str(x["year-max"])+" ")


    # 8 / 9 note
    if "note-min" in x and "note-max" in x and x["note-min"]!=None and x["note-max"]!=None: l.append(' note in range('+str(x["note-min"])+','+str(x["note-max"])+') ')
    elif "note-min" in x and x["note-min"]!=None: l.append(' note >= '+str(x["note-min"])+" ")
    elif "note-max" in x and x["note-max"]!=None: l.append(' note <= '+str(x["note-max"])+" ")

    # 10 / 11 nnote
    if "nnote-min" in x and "nnote-max" in x and x["nnote-min"]!=None and x["nnote-max"]!=None: l.append(' nnote in range('+str(x["nnote-min"])+','+str(x["nnote-max"])+') ')
    elif "nnote-min" in x and x["nnote-min"]!=None: l.append(' nnote >= '+str(x["nnote-min"])+" ")
    elif "nnote-max" in x and x["nnote-max"]!=None: l.append(' nnote <= '+str(x["nnote-max"])+" ")

    # 12 / 13 nreview
    if "nreview-min" in x and "nreview-max" in x and x["nreview-min"]!=None and x["nreview-max"]!=None: l.append(' nreview in range('+str(x["nreview-min"])+','+str(x["nreview-max"])+') ')
    elif "nreview-min" in x and x["nreview-min"]!=None: l.append(' nreview >= '+str(x["nreview-min"])+" ")
    elif "nreview-max" in x and x["nreview-max"]!=None: l.append(' nreview <= '+str(x["nreview-max"])+" ")

    # 15 / 16 duration
    if  "duration-min" in x and "duration-max" in x and x["duration-min"]!=None and x["duration-max"]!=None: l.append(' duration in range('+str(x["duration-min"])+','+str(x["duration-max"])+') ')
    elif  "duration-min" in x and x["duration-min"]!=None: l.append(' duration >= '+str(x["duration-min"])+" ")
    elif  "duration-max" in x and x["duration-max"]!=None: l.append(' duration <= '+str(x["duration-max"])+" ")

    #17
    if "actor" in x and x["actor"]!=None: l.append('"'+unquote_plus(x["actor"])+'" in actor ')

    #18
    if "director" in x and x["director"]!=None: l.append(' director like "%%'+unquote_plus(x["director"])+'%%" ')

    #19
    if "tosee" in x and x["tosee"]!=None: l.append(' tosee '+("=" if x["tosee"] else "!=") + " True ")

    #20
    if "seen" in x and x["seen"]!=None: l.append(' seen '+("=" if x["seen"] else "!=") + " True ")

    base = ""
    for i in range(len(l)):
        base+=("and" if i>0 else "")+l[i]
    if len(l)==0: base+="True"
    base+=" "



    if "order" in x and "order-sort" in x and x["order"]!=None and x["order-sort"]!=None:
        base+=" order by "+ x["order"]+" "
        if x["order-sort"]=="desc": base+="desc "

    if "rand" in x and x["rand"]!=None and x["rand"]>0:
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

    SHORT_REQUESTS={
        "toseeagain" : ("select * where tosee = True and seen = True order by note desc", "A revoir"),
        "tosee"  : ("select * where tosee = True and seen != True order by note desc", "A voir"),
        "seen"  : ("select * where seen = True order by note desc", "Vus")
    }

    def serve(self, req, res, file):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        res.serve_file_gen(config.www(file), self.userlist_object(currentuser.name))



    def __init__(self, file):
        RESTServer.__init__(self, attrs={"mode" : HTTPServer.SPAWN_THREAD})
        self.requests={}
        self.db = DB(file)
        self.users=self.db.get_users()
        self.sessions={}
        self.route("GET", "/", lambda req, res: self.serve(req, res, "index.html"))
        self.route("GET", "/index.html", lambda req, res: self.serve(req, res, "index.html"))
        self.route("GET", "/userlist", lambda req, res: self.serve(req, res, "user_list.html"))
        self.route("GET", "/request", lambda req, res: self.serve(req, res, "request.html"))
        self.route("GET", "/login",  lambda req, res: res.serve_file_gen(config.www("login.html")))
        self.route("POST", "/login",  self.handle_post_login)
        self.route("GET", "/import", lambda req, res: self.serve(req, res, "import.html"))

        self.route("POST", "/import", self.handle_import)
        self.route("GET", "/export", self.handle_export)
        self.route("GET", "/director/#id", self.handle_director)
        self.route("GET", "/actor/#id", self.handle_actor)
        self.route("GET", "/film/#id", self.handle_film)
        self.route("POST", "/film/#id", self.handle_film_modify)
        self.route("GET", "/results/#id/#page", self.handle_results)
        self.route("GET", "/results/#id/export/#format/#filename", self.handle_results_export)
        self.route("POST", "/results", self.handle_results)


        self.route("GET", "/showlist/#id", self.handle_show_list)
        self.route("GET", "/showlist/#id/#page", self.handle_show_list)

        self.route("GET", "/short/#id", self.handle_short)

        self.route("GET", "/request/#name", self.handle_get_request)
        self.route("GET", "/request/#name/run", self.handle_run_request)
        self.route("POST", "/request/#name", self.handle_create_request)
        self.route("DELETE", "/request/#name", self.handle_delete_request)

        self.route("GET", "/autocomplete/#type/#match", self.handle_autocomplete)
        self.route("GET", "/autocomplete/#type/#match/#max", self.handle_autocomplete)

        self.route("GET", "/searchfilm/#id", self.handle_search_film)

        self.route("GET", "/list", self.handle_list_all)
        self.route("GET", "/list/create/#name", self.handle_list_create)
        self.route("GET", "/list/#idl", self.handle_list_get)
        self.route("GET", "/list/#idl/remove", self.handle_list_remove)
        self.route("GET", "/list/#idl/rename/#name", self.handle_list_rename)
        self.route("GET", "/list/#idl/add/#idfilm", self.handle_list_add)
        self.route("GET", "/list/#idl/up/#idfilm", self.handle_list_up)
        self.route("GET", "/list/#idl/down/#idfilm", self.handle_list_down)
        self.route("GET", "/list/#idl/remove/#idfilm", self.handle_list_remove_item)


        self.route("GET", "/stop", self.handle_stop)
        self.route("GET", "/nop", self.handle_nop)


        self.static("/", config.WWW_DIR)

    def set_new_session(self, user):
        """for key in list(self.sessions.keys()):
            if self.sessions[key]==self.users[user]:
                del self.sessions[key]"""
        cookie=new_key(4)
        self.sessions[cookie]=self.users[user]
        return cookie

    def get_user(self, req: HTTPRequest, res: HTTPResponse, isjson=True):
        log.error("get_user(%s)" % str(tuple(req.cookies.keys())))
        if "SID" in req.cookies:
            cookie=req.cookies["SID"]
            if cookie in self.sessions:
                log.error("Authentification OK")
                return self.sessions[cookie]
            log.error("Authentification FAIL '%s' not in (%s)" % (cookie, str(tuple(self.sessions.keys()))))
        else:
            log.error("Authentification FAIL pas de SID")
        if isjson:
            res.content_type("application/json")
            res.serveJson({ "message" : "Erreur, session invalide", "code": 401}, 401)
        else:
            res.serve301("/login")
        return None

    def handle_nop(self, req: HTTPRequest, res: HTTPResponse):
        self.stop()
        pass

    def handle_stop(self, req: HTTPRequest, res: HTTPResponse):
        self.stop()
        requests.get("http://localhost:%d/nop" % self._port)

    def handle_search_film(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=req.params["id"]
        if str(id) in self.db.ids:
            row=self.db.ids[str(id)]
            year=row.resolve("year")
            if not year or year<=1900: year=None
            title=row.resolve("name")
            res.end(filmfinder.find_film(title, year), "application/json")
        else: res.serve404()

    def handle_post_login(self, req: HTTPRequest, res: HTTPResponse):
        js=req.body_json()
        user=js["login"]
        password=js["password"]
        res.content_type("application/json")
        if user in self.users:
            if utils.check_password(password, self.users[user].password):
                cookie = self.set_new_session(user)
                res.header("Set-Cookie", "SID=%s; Path=/" % cookie)
                res.end({})
                return
        res.serve401(data={"message" : "Login ou mot de passe invalide"})


    def handle_list_all(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        x=self.db.list_get(currentuser.name)
        res.end(x, "application/json")

    def handle_list_create(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        name=req.params["name"]
        l=AlloList(name=name)
        self.db.list_create("fanch", currentuser.name)

    def handle_list_get(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=req.params["idl"]
        x=self.db.get_list_by_id(currentuser.name, id)
        if x:
            res.end(x.moustache(), "application/json")
            raise Exception("ICI")
        else:
            res.serve404()

    def handle_list_remove(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        self.db.list_remove(currentuser.name, id)

    def handle_list_add(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        idfilm = req.params["idfilm"]
        self.db.list_add_item(currentuser.name, int(idfilm), id)


    def handle_list_up(self, req: HTTPRequest, res: HTTPResponse):
        pass

    def handle_list_down(self, req: HTTPRequest, res: HTTPResponse):
        pass

    def handle_list_rename(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        name = req.params["name"]
        self.db.list_rename(currentuser.name, id, name)

    def handle_list_remove_item(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        idfilm = int(req.params["idfilm"])
        self.db.list_remove_item(currentuser.name, id, idfilm)

    def _check_query(self, req, query):
        if "type" in req.query:
            type=req.query["type"]
            order=req.query["order"] if "order" in req.query else ""
            query.sort(type, order!="desc")
        if "pagesize" in req.query:
            query.pagesize=int(req.query["pagesize"])
            query.page=0

    def handle_export(self, req: HTTPRequest, res: HTTPResponse):
        pass

    def handle_director(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"].replace("+", " ")
        if not id in self.db.directors: return res.serve404()
        path = config.www("results.html")
        tmp = Request(self.db.row_from_director(id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, {"name" : id})))

    def handle_import(self, req: HTTPRequest, res: HTTPResponse):
        f=req.multipart_next_file()
        #f.save(config.user("fanch"), forcePath=True)
        x=f.parse_content()
        pass

    def handle_actor(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"].replace("+", " ")
        if not id in self.db.actors: return res.serve404()
        path = config.www("results.html")
        tmp = Request(self.db.row_from_actor(id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, { "name" : id})))


    def handle_film(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=req.params["id"]

        path = config.www("film.html")
        tmp = Request(self.db.get_film_by_id(currentuser.name,id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        self.requests[x.id] = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))

    def handle_film_modify(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=int(req.params["id"])
        js = req.body_json()
        if not js: return res.serve400()
        self.db.set(currentuser.name, js, id)

    def userlist_object(self, name, *args):
        x=self.db.list_get(name)
        l=[]
        for i in x: l.append(i)

        xr = self.db.request_get(name)
        lr=[]
        for i in xr: lr.append(i)
        return dictassign({ "user_list" : x,
                            "user_list_array" : l,
                            "requests" : xr,
                            "requests_list" : lr}, *args)

    def handle_show_list(self, req : HTTPRequest, res : HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        page = 0
        pagesize = AlloServer.RESULT_PER_PAGE
        if "page" in req.params: page=int(req.params["page"]-1)
        id = req.params["id"]
        x=self.db.list_get_films(currentuser.name, id)
        tmp=Request(x)
        x=tmp.result
        x.pagesize = 50
        self.requests[x.listid]=tmp
        x.page=page

        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))


    def handle_short(self, req : HTTPRequest, res : HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        short=AlloServer.SHORT_REQUESTS[req.params["id"]]
        tmp = Request(self.db.execute(short[0]))
        x = tmp.result
        x.pagesize = 10
        self.requests[x.id] = tmp
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, {"name" : short[1]})))

    def handle_autocomplete(self, req : HTTPRequest, res : HTTPResponse):
        type = req.params["type"]
        match = req.params["match"]
        max = int(req.params["max"]) if "max" in req.params else -1
        res.serveJson(self.db.autocomplete(match,type, max))


    def handle_results_export(self, req : HTTPRequest, res : HTTPResponse):
        if "id" in req.params and req.params["id"] in self.requests:
            x = self.requests[req.params["id"]].result
            data=""
            format=req.params["format"]
            filename=req.params["filename"]
            if format == "csv" :
                data=str(x)
                res.header("Content-Type", "text/csv")
            elif format == "json" :
                data=x.moustache()
                res.header("Content-Type", "application/json")
            res.header("Content-Disposition", "attachment; filename=\"%s\"" % filename)
            res.end(data)
        else:
            return res.serve400()

    def handle_results(self, req : HTTPRequest, res : HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        request = ""
        pagesize = AlloServer.RESULT_PER_PAGE
        if req.method=="POST":
            body=req.body_json()
            if "json" in body:
                bodyjson=json.loads(body["json"])
                if "nperpage" in bodyjson:
                    pagesize = int(bodyjson["nperpage"])
                request=json_to_request(bodyjson)
            elif "text" in body:
                request=unquote_plus(body["text"])
            tmp=Request(self.db.find(currentuser.name, request))
            x=tmp.result
            x.pagesize = pagesize
            self.requests[x.id]=tmp
        else:
            if "id" in req.params and "page" in req.params and req.params["id"] in self.requests:
                x=self.requests[req.params["id"]].result
                x.page=int(req.params["page"])-1
            else:
                return res.serve400()

        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))

    def handle_get_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        res.serve_file_gen(config.www("index.html"), self.userlist_object(currentuser.name,{
            "run" : req.params["name"]
        }))

    def handle_run_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        name = req.params["name"]
        #args = self.db.userdata.requests[name]["values"]
        args = self.db.request_get(currentuser.name, name)
        request = json_to_request(args)
        tmp = Request(self.db.find(currentuser.name, request))
        x = tmp.result
        x.pagesize = args["nperpage"] if "nperpage" in args else 20
        self.requests[x.id] = tmp
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))



    def handle_create_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        self.db.request_add(currentuser.name, req.params["name"], req.body_json())

    def handle_delete_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        self.db.request_remove(currentuser.name, req.params["name"])

filecache.init()


browser=None
port=8080
logfile=sys.stdout
if len(sys.argv)>2:
    i=1
    while i< len(sys.argv):
        arg=sys.argv[i]
        if arg=="-b" or arg=="--browser":
            browser=sys.argv[i+1]
            i+=1
        if arg=="-p" or arg=="--port":
            port=int(sys.argv[i+1])
            i+=1
        if arg=="-l" or arg=="--log":
            logfile=open(sys.argv[i+1], "w")
            i+=1
        i+=1



Log.init()
"""
from sqlite_connector import create_datase
create_datase("db/allodb.db", "db.json", "fanch")"""


als = AlloServer("db/allodb.db")
if not browser:
    als.listen(port)
else:
    if os.fork():
        als.listen(port)
        als.db.userdata.save()
    else:
        os.system("%s 'http://localhost:%d' " % (browser,port))