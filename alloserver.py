import json
import os
import time
import sys

import requests
import user
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
            tmp+=(x["pays-op"] if i>0 else "")+' nationality like "%%'+unquote_plus(arr[i])+'%%" '
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
    if "year-min" in x and x["year-min"]!=None: l.append(' year >= '+str(x["year-min"])+" ")
    if "year-max" in x and x["year-max"]!=None: l.append(' year <= '+str(x["year-max"])+" ")


    # 8 / 9 note
    if "note-min" in x and x["note-min"]!=None: l.append(' note >= '+str(x["note-min"])+" ")
    if "note-max" in x and x["note-max"]!=None: l.append(' note <= '+str(x["note-max"])+" ")

    # 10 / 11 nnote
    if "nnote-min" in x and x["nnote-min"]!=None: l.append(' nnote >= '+str(x["nnote-min"])+" ")
    if "nnote-max" in x and x["nnote-max"]!=None: l.append(' nnote <= '+str(x["nnote-max"])+" ")

    # 12 / 13 nreview
    if "nreview-min" in x and x["nreview-min"]!=None: l.append(' nreview >= '+str(x["nreview-min"])+" ")
    if "nreview-max" in x and x["nreview-max"]!=None: l.append(' nreview <= '+str(x["nreview-max"])+" ")

    # 15 / 16 duration
    if  "duration-min" in x and x["duration-min"]!=None: l.append(' duration >= '+str(x["duration-min"])+" ")
    if  "duration-max" in x and x["duration-max"]!=None: l.append(' duration <= '+str(x["duration-max"])+" ")

    #17
    if "actor" in x and x["actor"]!=None: l.append(' actor like "%%'+unquote_plus(x["actor"])+'%%" ')

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
        if x["order"]!="shuffle":
            base+=" order by "+ x["order"]+" "
            if x["order-sort"]=="desc": base+="desc "

    #if "rand" in x and x["rand"]!=None and x["rand"]>0:
    #    base="rand("+base+", "+str(x["rand"])+" ) "


    log.info("Request = ", base)
    return base

class Request:
    def __init__(self, result):
        self.id=result.id
        self.result=result
        self.time=time.time()


API_ROOT = "/api"

class AlloServer(RESTServer):
    RESULT_PER_PAGE=10

    SHORT_REQUESTS={
        "toseeagain" : ("select * where tosee = True and seen = True order by note desc", "A revoir"),
        "tosee"  : ("select * where tosee = True and seen != True order by note desc", "A voir"),
        "seen"  : ("select * where seen = True order by note desc", "Vus")
    }


    def __init__(self, file):
        RESTServer.__init__(self, attrs={"mode" : HTTPServer.SPAWN_THREAD})
        self.db = DB(file)
        self.users=self.db.get_users()
        self.sessions={}
        self.route("GET", "/", lambda req, res: self.serve(req, res, "index.html"))
        self.route("GET", "/index.html", lambda req, res: self.serve(req, res, "index.html"))
        self.route("GET", "/userlist", lambda req, res: self.serve(req, res, "user_list.html"))
        self.route("GET", "/request", lambda req, res: self.serve(req, res, "request.html"))
        self.route("GET", "/login",  lambda req, res: res.serve_file_gen(config.www("login.html")))
        self.route("POST", "/login",  self.html_handle_post_login)
        self.route("GET", "/import", lambda req, res: self.serve(req, res, "import.html"))
        self.route("POST", "/import", self.html_handle_import)
        self.route("GET", "/film/#id", self.html_handle_film)
        self.route("GET", "/director/#id", self.html_handle_director)
        self.route("GET", "/actor/#id", self.html_handle_actor)
        self.route("GET", "/results/#id/#page", self.html_handle_results)
        self.route("POST", "/results", self.html_handle_results)
        self.route("GET", "/showlist/#id", self.html_handle_show_list)
        self.route("GET", "/showlist/#id/#page", self.html_handle_show_list)
        self.route("GET", "/searchfilm/#id", self.html_handle_search_film)
        self.route("GET", "/short/#id", self.html_handle_short)
        self.route("GET", "/request/#name/run", self.html_handle_run_request)
        self.route("GET", "/request/#name" , self.html_handle_get_request)
        self.route("GET", "/disconnect" , self.html_handle_disconnect)

        self.route("POST", "%s/import" % API_ROOT, self.api_handle_import)
        self.route("GET", "%s/export" % API_ROOT, self.api_handle_export)
        self.route("GET", "%s/results/#id/export/#format/#filename" % API_ROOT, self.api_handle_results_export)

        self.route("POST", "%s/film/#id" % API_ROOT, self.api_handle_film_modify)
        self.route("GET", "%s/film/#id" % API_ROOT, self.api_handle_film_get)

        self.route("DELETE", "%s/request/#name" % API_ROOT, self.api_handle_delete_request)
        self.route("POST", "%s/request/#name" % API_ROOT, self.api_handle_create_request)
        self.route("POST", "%s/request" % API_ROOT, self.api_handle_request)

        self.route("GET", "%s/autocomplete/#type/#match" % API_ROOT, self.api_handle_autocomplete)
        self.route("GET", "%s/autocomplete/#type/#match/#max" % API_ROOT, self.api_handle_autocomplete)


        self.route("GET", "%s/list" % API_ROOT, self.api_handle_list_all)
        self.route("GET", "%s/list/create/#name" % API_ROOT, self.api_handle_list_create)
        self.route("GET", "%s/list/#idl" % API_ROOT, self.api_handle_list_get)
        self.route("GET", "%s/list/#idl/remove" % API_ROOT, self.api_handle_list_remove)
        self.route("GET", "%s/list/#idl/rename/#name" % API_ROOT, self.api_handle_list_rename)
        self.route("GET", "%s/list/#idl/add/#idfilm" % API_ROOT, self.api_handle_list_add)
        self.route("GET", "%s/list/#idl/up/#idfilm" % API_ROOT, self.api_handle_list_up)
        self.route("GET", "%s/list/#idl/down/#idfilm" % API_ROOT, self.api_handle_list_down)
        self.route("GET", "%s/list/#idl/remove/#idfilm" % API_ROOT, self.api_handle_list_remove_item)


        self.route("GET", "/stop", self.handle_stop)
        self.route("GET", "/nop", self.handle_nop)


        self.static("/", config.WWW_DIR)


    #
    #  ==== Utils methods
    #
    def api_resp(self, res : HTTPResponse, httpcode, code, msg, data=None):
        res.serv(httpcode, {"Content-Type", "application/json"}, {
            "code" : code,
            "message" : msg,
            "data" : data
        })


    def api_resp_ok(self, res : HTTPResponse, data=None):
        res.serv(200, {"Content-Type" : "application/json"}, {
            "code" : 0,
            "message" : "Success",
            "data" : data
        })

    def serve(self, req, res, file):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        res.header("Cache-Control", "no-cache")
        res.header("Pragma", "no-cache")
        res.header("Expires", "0")
        res.serve_file_gen(config.www(file), self.userlist_object(currentuser.name))



    def set_new_session(self, user):
        """for key in list(self.sessions.keys()):
            if self.sessions[key]==self.users[user]:
                del self.sessions[key]"""
        cookie=new_key(4)
        self.sessions[cookie]=self.users[user]
        return cookie

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


    def _check_query(self, req, query):
        #post
        if req.body and "json" in req.body:
            jsquery=json.loads(req.body["json"])
            if "order" in jsquery:
                type=jsquery["order"]
                order=""
                if "order-sort" in jsquery:
                    order=jsquery["order-sort"]
                query.sort(type, order!="desc")
            if "nperpage" in jsquery:
                query.pagesize = int(jsquery["nperpage"])
                query.page = 0
            if "rand" in jsquery:
                query.rand_select(jsquery["rand"])



        # get
        if req.method.lower()=="get":
            if "type" in req.query:
                type=req.query["type"]
                order=req.query["order"] if "order" in req.query else ""
                query.sort(type, order!="desc")
            if "pagesize" in req.query:
                query.pagesize=int(req.query["pagesize"])
                query.page=0

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
            res.serve302("/login")
        return None

    def handle_nop(self, req: HTTPRequest, res: HTTPResponse):
        self.stop()
        pass

    def handle_stop(self, req: HTTPRequest, res: HTTPResponse):
        self.stop()
        requests.get("http://localhost:%d/nop" % self._port)


    #
    #  ==== HTML Handlers
    #


    def html_handle_search_film(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"]
        row=self.db.find(currentuser.name, "id=%s" % id)
        if row:
            row=row.row_at(0)
            year=row[4]
            title=row[1]
            res.end(filmfinder.find_film(title, year), "application/json")
        else: res.serve404()


    def html_handle_run_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        name = req.params["name"]
        #args = self.db.userdata.requests[name]["values"]
        args = self.db.request_get(currentuser.name, name)
        req.body={"json": json.dumps(args["values"])}
        request = json_to_request(args["values"])
        tmp = Request(self.db.find(currentuser.name, request))
        x = tmp.result
        x.pagesize = args["nperpage"] if "nperpage" in args else 20
        currentuser.request = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))

    def html_handle_director(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"].replace("+", " ")
        path = config.www("results.html")
        tmp = Request(self.db.find(currentuser.name, "director like '%%%s%%'" % id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        currentuser.request = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, {"name" : id})))


    def html_handle_post_login(self, req: HTTPRequest, res: HTTPResponse):
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

    def html_handle_actor(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"].replace("+", " ")
        path = config.www("results.html")
        tmp = Request(self.db.find(currentuser.name,"actor like '%%%s%%'" % id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        currentuser.request=tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, { "name" : id})))

    def html_handle_show_list(self, req : HTTPRequest, res : HTTPResponse):
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
        currentuser.request=tmp
        x.page=page

        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))


    def html_handle_short(self, req : HTTPRequest, res : HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        path = config.www("results.html")
        short=AlloServer.SHORT_REQUESTS[req.params["id"]]
        tmp = Request(self.db.execute(short[0]))
        x = tmp.result
        x.pagesize = 10
        currentuser.request = tmp
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name, {"name" : short[1]})))



    def html_handle_film(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        id=req.params["id"]

        path = config.www("film.html")
        tmp = Request(self.db.get_film_by_id(currentuser.name,id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        currentuser.request = tmp
        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))


    def html_handle_results(self, req : HTTPRequest, res : HTTPResponse):
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
            currentuser.request=tmp

        else:
            if "id" in req.params and "page" in req.params:
                x=currentuser.request.result
                x.page=int(req.params["page"])-1
            else:
                return res.serve400()



        self._check_query(req, x)
        res.serve_file_gen(path, x.moustache(self.userlist_object(currentuser.name)))


    def html_handle_get_request(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        res.serve_file_gen(config.www("index.html"), self.userlist_object(currentuser.name,{
            "run" : req.params["name"]
        }))

    def html_handle_disconnect(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        del self.sessions[req.cookies["SID"]]
        res.serve302("/login")


    def html_handle_import(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        f=req.multipart_next_file()
        x=json.loads(f.parse_content().decode("ascii"))
        currentuser.replace_from_js(x)
        res.serve302("/")

    #
    #  ==== API Handlers
    #

    def api_handle_list_all(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list) : renvoie toutes les liste de l'utilisateur
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        x=self.db.list_get(currentuser.name)
        self.api_resp_ok(res, x)

    def api_handle_list_create(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list/#name) : Crée une nouvelle list #create
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        name=req.params["name"]
        l=AlloList(name=name)
        self.db.list_create("fanch", name)
        self.api_resp_ok(res)

    def api_handle_list_get(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list/#idl) : Renvoie la liste avec l'ID #idl sous format json
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=req.params["idl"]
        x=self.db.get_list_by_id(currentuser.name, id)
        if x:
            res.end(x.moustache(), "application/json")
            raise Exception("ICI")
        else:
            res.serve404()
        self.api_resp_ok(res)

    def api_handle_list_remove(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list/#idl/remove) : Supprime la liste avec l'ID #idl
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        self.db.list_remove(currentuser.name, id)
        self.api_resp_ok(res)

    def api_handle_list_add(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list/#idl/add/#idfilm) : Ajoute le film par son identifiant (#idfilm) à la liste #idl
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        idfilm = req.params["idfilm"]
        self.db.list_add_item(currentuser.name, int(idfilm), id)
        self.api_resp_ok(res)


    def api_handle_list_up(self, req: HTTPRequest, res: HTTPResponse):
        pass

    def api_handle_list_down(self, req: HTTPRequest, res: HTTPResponse):
        pass

    def api_handle_list_rename(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/list/#idl/rename/#name) : Change le nom de la liste #idl par #name
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        name = req.params["name"]
        self.db.list_rename(currentuser.name, id, name)
        self.api_resp_ok(res)

    def api_handle_list_remove_item(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (/api/) :
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id = req.params["idl"]
        idfilm = int(req.params["idfilm"])
        self.db.list_remove_item(currentuser.name, id, idfilm)
        self.api_resp_ok(res)



    def api_handle_export(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        payload=currentuser.export()
        res.serve_file_data(payload, "application/json", currentuser.name+".json", forceDownload=True)


    def api_handle_import(self, req: HTTPRequest, res: HTTPResponse):
        currentuser=self.get_user(req, res)
        if not currentuser: return
        f=req.multipart_next_file()
        x=json.loads(f.parse_content().decode("ascii"))
        usr=currentuser.replace_from_js(x)
        self.api_resp_ok(res)


    def api_handle_film_modify(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (POST /api/film/#id) : Modifie le film #id (id allocine) avec le contenu du parametre post.
        Le parametre post est un objet ou les clés correspondent aux colonnes sql et les valeurs de l'objet seront
        modifiées dans la base
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        id=int(req.params["id"])
        js = req.body_json()
        if not js: return res.serve400()
        self.db.set(currentuser.name, js, id)
        self.api_resp_ok(res)



    def api_handle_autocomplete(self, req : HTTPRequest, res : HTTPResponse):
        """
        Méthode API (GET /api/autocomplete/#type/#match[/#max]) :
            Renvoie une liste (tronqué à la taille maximum #max si passé) qui correspondent aux résultat
            #match sur la recherche de la colonne #type
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        type = req.params["type"]
        match = req.params["match"]
        max = int(req.params["max"]) if "max" in req.params else -1
        self.api_resp_ok(res,self.db.autocomplete(match,type, max))


    def api_handle_results_export(self, req : HTTPRequest, res : HTTPResponse):
        """
        Méthode API (/api/) :
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res, False)
        if not currentuser: return
        if "id" in req.params:
            x = currentuser.request.result
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



    def api_handle_request(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (POST /api/request/#format) : Lance une requete #format vaut soit "json" soit "sql"
            Le le format de la requete si format=json
            {
                "fields" : {
                    "CHAMP1" : "VALEUR1",
                    "CHAMP2" : "VALEUR2",
                    ...
                    "CHAMPn" : "VALEURn"
                }
            }
            ou format=sql
            {
                "request" : "REQUETE"
            }
            La valeur de "request" corresond juste a une expression boolen (pas de select .. from)
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return




    def api_handle_film_get(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (GET /api/film/#id) : Récupère le contenu d'un film à l'id #id
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return

        id=req.params["id"]

        tmp = Request(self.db.get_film_by_id(currentuser.name,id))
        x = tmp.result
        x.pagesize = AlloServer.RESULT_PER_PAGE
        currentuser.request = tmp
        self._check_query(req, x)
        self.api_resp_ok(res, x.moustache())






    def api_handle_create_request(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (POST /api/request/#name) : Enregistre une requete au nom de #name.
            Le contenu de la requete (en POST) est suit ce format:
            {
                "name" : "NOM DE LA REQUETE",
                "fields" : [CHAMPS A AFFICHER],
                "values" : {
                    "CHAMP1" : "VALEUR1",
                    "CHAMP2" : "VALEUR2",
                    ...
                    "CHAMPn" : "VALEURn",
                }
            }
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        self.db.request_add(currentuser.name, req.params["name"], req.body_json())
        self.api_resp_ok(res)

    def api_handle_delete_request(self, req: HTTPRequest, res: HTTPResponse):
        """
        Méthode API (DELETE /api/request/#name) : Supprime la requete #name
        :param req: La requête
        :param res: La réponse
        :return: Rien
        """
        currentuser=self.get_user(req, res)
        if not currentuser: return
        self.db.request_remove(currentuser.name, req.params["name"])
        self.api_resp_ok(res)


filecache.init()


browser=None
create_user=None
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
        if arg=='-u' or arg=="--user":
            create_user=sys.argv[i+1]
            i+=1
        i+=1



Log.init()
"""
from sqlite_connector import create_datase
create_datase("db/allodb.db", "db.json", "fanch")"""






if create_user:
    adb = DB("db/allodb.db")
    js=None
    with open(create_user) as f:
        js=json.loads(f.read())
    user.User.import_user(adb, js)
    adb.commit()
else:
    als = AlloServer("db/allodb.db")
    if not browser:
        als.listen(port)
    else:
        if os.fork():
            als.listen(port)
            als.db.userdata.save()
        else:
            os.system("%s 'http://localhost:%d' " % (browser,port))
"""
db = DB.create_from_file("db/test.db", "db.json")
usr = user.User.import_user_file(db, "user/fanch2.json")
db.commit()
"""
