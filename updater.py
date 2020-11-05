import json
import math
import os
import sqlite3
import threading
import time, requests, alloimport

import log
from log import Log
from sqlite_connector import SQConnector

import allodb

def formattime(t):
    s=0
    m=0
    h=0
    if t>=3600:
        h=int(t/3600)
        t=t%3600
    if t>=60:
        m=int(t/60)
        t=t%60
    s=t
    out=""
    if h: out+="%d h " % h
    if m: out+="%d m " % m
    return out+"%d s " % s



class AlloUpdater(SQConnector):
    COLUMNS = [
        ("id", int, -1, "id"),
        ("name", None, "", "name"),
        ("image/url", None, "", "image"),
        ("pays/*", alloimport.castpays, [], "nationality"),
        ("annee", None, 0, "year"),
        ("duration", alloimport.castduration, 0, "duration"),
        ("genre/*", alloimport.castarr, [], "genre"),
        ("description", None, "", "description"),
        ("director/*/name", None, [], "director"),
        ("actor/*/name", alloimport.castarr, [], "actor"),
        ("creator/*/name", alloimport.castarr, [], "creator"),
        ("musicBy/*/name", alloimport.castarr, [], "musicBy"),
        ("aggregateRating/ratingValue", alloimport.floatvirg, 0, "note"),
        ("aggregateRating/ratingCount", int, 0, "nnote"),
        ("aggregateRating/reviewCount", int, 0, "nreview")
    ]
    #URl_DL="http://localhost/allocine/%d.html"
    URl_DL="https://www.allocine.fr/film/fichefilm_gen_cfilm=%d.html"
    UPDATE_SCHEM="""create table update_list(
                filmid int,
                timestamp int,
                priority int,
                needupdate int,
                foreign key(filmid) references films(id)
            );
            """
    TO_UPDATE_SCHEM="""create table to_update(
                filmid int,
                priority int,
                foreign key(filmid) references films(id)
            );
            """
    VAR_SCHEM="""create table var(
                key text,
                value int
            );
            """
    N_TO_DISCOVER=1000

    @staticmethod
    def calc_prio(a, b, raw, t):
        """
        Calcul la priorité de la prochain mise à jour [0-640]
        :param a: nnote avant update
        :param b: nnote apres update
        :param raw: row après update
        :param t: temmps en seconde depuis la derniere update
        :return: prio
        """
        if not a: a = 1
        if not b: b = 1
        if t:
            t /= 3600 * 24 * 30.0  # par mois
            pc = (100 * (b) / a) ** (1 / max(0.01,t))  # augmentation de note (en pourcentage/mois)
        else:
            pc=1

        r = min(pc, 10) * 10 * min(math.log(b, 10), 4) if pc else 0
        return r + (r * ((raw[12] + 1) / 10))


    def __init__(self, path="db/update.db", nthread=0):
        SQConnector.__init__(self, path)
        self.varcache={}
        self.init()
        self.queue=[]
        self.maxtryed=self.one("select max(id) from films")
        log.i("Max try = %d" % self.maxtryed)



    def maxtry(self, n=None):
        x=0
        if n>self.maxtryed: self.maxtryed=n
        x=self.maxtryed
        return x



    def enqueue(self, x):
        self.queue.append(x)


    def queue_length(self):
        x=len(self.queue)
        return x

    def dequeue(self):
        if len(self.queue)>0:
            x=self.queue[0]
            del self.queue[0]
        else:
            x= None
        return x



    def update(self, filmid):
        js=None
        needupdate=True
        action=""
        try:
            js=self.get_film(filmid)
        except:
            return False


        try:
            action = "select count(*) from update_list where filmid=%d" % filmid
            if not self.one(action):
                prio=AlloUpdater.calc_prio(0,js[13],js, 0)
                action = "insert into update_list (filmid, timestamp, priority, needupdate) values (%d, %d, %d, %d)" %(
                    filmid, int(time.time()), prio, int(needupdate)
                )
                self.exec(action)
                self.insert_film_base(js)
            else:
                action = "select nnote from films where id=%d" % filmid
                old=self.one(action)
                action = "select timestamp from update_list where filmid=%d" % filmid
                t=time.time()-self.one(action)
                prio=AlloUpdater.calc_prio(old, js[13], js, t)
                action="update update_list set timestamp=%d, priority=%d, needupdate=%d where filmid=%d" % (
                    int(time.time()), prio, int(needupdate), filmid
                )
                self.exec(action)
                self.update_film_base(js)
            return True
        except sqlite3.IntegrityError as err:
            return False
        except Exception as err:
            log.c("%s (update) (%s) pour %s \n\tRequest = %s " % ( err.__class__.__name__, err, str(js[0]), action))
            self.commit()
            exit(-1)


    def init(self):
        if not self.table_exists("films") : self.exec(SQConnector.FILM_SCHEM)
        if not self.table_exists("update_list") : self.exec(AlloUpdater.UPDATE_SCHEM)
        if not self.table_exists("to_update") : self.exec(AlloUpdater.TO_UPDATE_SCHEM)
        if not self.table_exists("var"):
            self.exec(AlloUpdater.VAR_SCHEM)
            self.var_set("last_complete_update", 0)
            self.var_set("last_update", 0)
            self.var_set("do_complete_update", 0)
            self.var_set("do_update", 0)



    def get_film(self, n):
        url = AlloUpdater.URl_DL % n
        print(url)
        ret=requests.get(url, headers={
            "Host": "www.allocine.fr",
            "User-Agent": "Mozilla/5.0 (X11; Linux x86_64; rv:81.0) Gecko/20100101 Firefox/81.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "fr,fr-FR;q=0.8,en-US;q=0.5,en;q=0.3",
            "Accept-Encoding": "gzip, deflate, br",
            "DNT": "1",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1",
            "Pragma": "no-cache",
            "Cache-Control": "no-cache"
        })
        with open("/home/fanch/index.html", "wb") as f:
            f.write(ret.content)

        if ret.status_code==200:
            js = alloimport.extract(ret.content.decode("utf-8"), AlloUpdater.COLUMNS)
            js[0]=n
            print(js)
            return js
        raise Exception("%s" % url)

    def export(self, filename):
        db=self.exec("select * from films")
        with open(filename, "w") as f:
            f.write(json.dumps(db))

    def var_get(self, key):
        if key in self.varcache: return self.varcache[key]
        return self.one("select value from var where key='%s' " % key)

    def var_set(self, key, value):
        self.varcache[key]=value
        if self.one("select count(*) from var where key='%s' " % key)==0:
            if isinstance(value, str):
                self.exec("insert into var (key, value) values ('%s', '%s') " % (key, value))
            elif isinstance(value, (int, float) ):
                self.exec("insert into var (key, value) values ('%s', %s) " % (key, str(value)))
            else: raise Exception("Mauvais type pour la variable '%s' valeur : '%s' " % (key, str(value)))
        else:
            if isinstance(value, str):
                self.exec("update var  set value='%s' where key='%s'" % (value, key))
            elif isinstance(value, (int, float) ):
                self.exec("update var  set value='%s' where key='%s' " % (str(value), key))
            else: raise Exception("Mauvais type pour la variable '%s' valeur : '%s' " % (key, str(value)))
        self.commit()

    def _schedule_update(self):
        if time.time()-self.var_get("last_complete_update")> (30*24*3600):
            log.i("Programmation d'une mise a jour complete")

            dt=int(time.time()-(7*24*3600))
            ret=self.exec("select filmid from update_list where timestamp>%d order by timestamp asc" % dt)
            i=len(ret)+1
            for x in ret:
                self.exec("insert into to_update (filmid, priority) values (%d, %d) " % (x[0], i))
                i-=1
            self.var_set("last_complete_update", int(time.time()))
            self.var_set("do_complete_update", 1)
        else:
            self.var_set("do_complete_update", 0)
        if time.time()-self.var_get("last_update")> (7*24*3600):
            log.i("Programmation d'une mise a jour de découverte")
            max=self.one("select max(id) from films")
            for i in range(self.N_TO_DISCOVER):
                self.exec("insert into to_update (filmid, priority) values (%d, %d) " % (max+i+1, max))
            self.var_set("last_update",  int(time.time()))
            self.var_set("do_update", 1)
        else:
            self.var_set("do_update", 0)




    def do_update(self, n):
        fid=self.dequeue()
        self.update(fid)
        self.exec("delete from to_update where filmid=%d " % fid)
        #log.debug("[tid:%d] %d done" % (tid, fid))
        if  n%50==0:
            log.d("COMMIT !")
            self.commit()



    def schedule(self):
        while True:
            if self.one("select count(*) from update_list")==0:
                self._schedule_update()
                self.commit()
                self.var_set("total_to_update", self.one("select count(filmid) from update_list"))
                log.d("To update : %d "% (self.var_get("total_to_update")))
            ret = self.exec("select filmid from update_list order by priority desc")
            log.d(ret)
            for x in ret:
                self.queue.append(x[0])


            n=0
            t=time.time()
            last=n
            while self.queue_length()>0:
                self.do_update(n)
                if n%50==0 and n and self.var_get("total_to_update"):
                    tmp=100-100*len(self.queue)/self.var_get("total_to_update")
                    if int(last*10)!=int(tmp*10):
                        est=(len(self.queue)/n)*(time.time()-t)
                        log.d("%.1f%% : %s" % (tmp, formattime(est)))
                        last=tmp
                n+=1

            self.commit()

            if self.one("select max(id) from films")+AlloUpdater.N_TO_DISCOVER/2<self.maxtryed:
                comp, up = self.var_get("do_complete_update"),self.var_get("do_update")
                if comp or up:
                    dt=time.time()
                    if comp: dt-=self.var_get("last_complete_update")
                    else: dt-=self.var_get("last_update")
                    log.i("fin de mise à jour complete en %d s...\n\n\n" % dt)
                    self.export("last.json")
                time.sleep(24*3600)


def do_update(lvl=Log.DEBUG, fd="updater.log"):
    Log.init(lvl, fd)
    try:
        with open("update.lock") as f:
            raise FileExistsError()
    except FileExistsError as e:
        log.c("Impossible de faire la mise à jour une est déja en cours...")
        #return False
    except FileNotFoundError as e:
        pass
    log.i("Création du fichier lock")
    with open("update.lock", "w") as f:
        pass
    x = AlloUpdater(nthread=0)
    x.schedule()
    #print(x.get_film(251315))
    log.e("Fermture du lock")
    os.remove("update.lock")
    Log.close()
    return True

def do_update_fork(lvl=Log.DEBUG, fd="updater.log"):
    pid = os.fork()
    if not pid:
        do_update(lvl, fd)
        exit(0)


if __name__ == "__main__":
    do_update()
    #while True:
    #    time.sleep(1)
