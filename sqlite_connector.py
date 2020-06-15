import os
import time
import json
import sqlite3
import resultset
from hashlib import sha3_512
import base64
import utils

def join(x):
    if isinstance(x, str): return x
    if isinstance(x, (tuple, list)): return ";".join(x)
    return ""



def _int(x):
    if isinstance(x, (int, float, str)): return int(x)
    return -1



FCTS = [
    _int,
    str,
    str,
    join,
    _int,
    _int,
    join,
    str,
    join,
    join,
    join,
    join,
    float,
    _int,
    _int
]
def _str(x):
    return str(x).replace("'", "\\'")

def jsdef(js, key, defaut="", fct=_str):
    if isinstance(js, (tuple, list)):
        if js[key]==None:
            if not fct: return defaut
            return fct(defaut)
        if not fct : return js[key]
        return fct(js[key])
    else:
        if key in js:
            if not fct: return js[key]
            return fct(js[key])
        if not fct: return defaut
        return fct(defaut)

def format_row(row):
    out = []
    for i in range(len(row)):
        out.append(FCTS[i](row[i]))
    return tuple(out)

def translate_query(src):
    i=0
    l=src.split(' ')
    out=""
    while i<len(l):
        x=l[i]
        if i+2<len(l) and l[i+1]=='in':
            out+=" %s like '%%%s%%' " % (l[i+2], l[i][1:-1])
            i+=3
        else:
            out+=x+" "
            i+=1

    return out


def sqvalue(x):
    if isinstance(x, str): return "'%s'" % x
    if isinstance(x, bool): return "true" if x else "false"
    if isinstance(x, int): return "%d" % x
    if isinstance(x, float): return "%f" % x
    raise Exception("Erreur type non compatible")

class SQConnector:
    FILM_SCHEM="""create table films (
	id int primary key,
    name text,
    image text,
    nationality text,
    year int,
    duration int,
    genre text,
    description text,
    director text,
    actor text,
    creator text,
    musicBy text,
    note real,
    nnote int,
    nreview int)
"""
    def __init__(self, file):
        self.conn=sqlite3.connect(file)
        self.conn.execute("PRAGMA case_sensitive_like = false;")

    def exec(self, sql):
        c=self.conn.cursor()
        return c.execute(sql).fetchall()

    def onerow(self, sql):
        c = self.conn.cursor()
        return c.execute(sql).fetchone()

    def one(self, sql):
        c = self.conn.cursor()
        return c.execute(sql).fetchone()[0]

    def resultset(self, sql, pagesize=50, page=0 ):
        cur = self.conn.cursor()
        rs = resultset.ResultSet(pagesize, page)
        cur.execute(sql)
        rs.set_results(cur)
        return rs

    def find(self, user, sql, order=None, pagesize=50, page=0):
        query="select * from films, %s where filmid=id and %s " % (user, translate_query(sql))
        if order:
            query+=" ORDER BY %s" % order
        cur=self.conn.cursor()
        rs=resultset.ResultSet(pagesize, page)
        cur.execute(query)
        rs.set_results(cur)
        return rs

    def insert_film_base(self, js):
        if isinstance(js, (tuple, list)):
            row=format_row(js)
            self.exec(
            "insert into films (id,name,image,nationality,year,duration,genre,description,director,actor,creator,musicBy,note,nnote,nreview) values %s;" % str(
                row))
        elif isinstance(js, (dict)):
            self.exec("""insert into films  (id,name,image,nationality,year,duration,genre,description,director,actor,creator,musicBy,note,nnote,nreview) values (
                %d, "%s", "%s", "%s", %s, %s, "%s", "%s", "%s", "%s", "%s", "%s", %s, %s, %s           
            """ % (
                int(js["id"]),
                jsdef(js, "name"),
                jsdef(js, "image"),
                jsdef(js, "nationality", fct=join),
                jsdef(js, "year", "NULL"),
                jsdef(js, "duration", "NULL"),
                jsdef(js, "genre", fct=join),
                jsdef(js, "description"),
                jsdef(js, "director", fct=join),
                jsdef(js, "actor", fct=join),
                jsdef(js, "creator", fct=join),
                jsdef(js, "musicBy", fct=join),
                jsdef(js, "note", "NULL"),
                jsdef(js, "nnote", "0"),
                jsdef(js, "nreview", "0")
            ))
        else: raise Exception("insert_film_base: dict, tuple ou list attendu")

    def update_film_base(self, js):
        if isinstance(js, (tuple, list)):
            self.exec("""update films set 
                            name="%s",
                            image="%s",
                            nationality="%s",
                            year=%s,
                            duration=%s,
                            genre="%s",
                            description="%s",
                            director="%s",
                            actor="%s",
                            creator="%s",
                            musicBy="%s",
                            note=%s,
                            nnote=%s,
                            nreview=%s  where id=%d           
                        """ % (
                jsdef(js, 1),
                jsdef(js, 2),
                jsdef(js, 3, fct=join),
                jsdef(js, 4, "NULL"),
                jsdef(js, 5, "NULL"),
                jsdef(js, 6, fct=join),
                jsdef(js, 7),
                jsdef(js, 8, fct=join),
                jsdef(js, 9, fct=join),
                jsdef(js, 10, fct=join),
                jsdef(js, 11, fct=join),
                jsdef(js, 12, "NULL"),
                jsdef(js, 13, "0"),
                jsdef(js, 14, "0"),
                int(js[0])
            ))
        elif isinstance(js, (dict)):
            self.exec("""update films set 
                name='%s',
                image='%s',
                nationality='%s',
                year=%s,
                duration=%s,
                genre='%s',
                description='%s',
                director='%s',
                actor='%s',
                creator='%s',
                musicBy='%s',
                note=%s,
                nnote=%s,
                nreview=%s  where id=%d           
            """ % (
                jsdef(js, "name"),
                jsdef(js, "image"),
                jsdef(js, "nationality", fct=join),
                jsdef(js, "year", "NULL"),
                jsdef(js, "duration", "NULL"),
                jsdef(js, "genre", fct=join),
                jsdef(js, "description"),
                jsdef(js, "director", fct=join),
                jsdef(js, "actor", fct=join),
                jsdef(js, "creator", fct=join),
                jsdef(js, "musicBy", fct=join),
                jsdef(js, "note", "NULL"),
                jsdef(js, "nnote", "0"),
                jsdef(js, "nreview", "0"),
                int(js["id"])
            ))
        else: raise Exception("update_film_base: dict, tuple ou list attendu")


    def init_base(self, file):
        with open(file, "r") as f:
            js=json.loads(f.read())
        self.exec(SQConnector.FILM_SCHEM)
        for row in js["data"]:
            row = format_row(row)
            try:
                self.exec("insert into films (id,name,image,nationality,year,duration,genre,description,director,actor,creator,musicBy,note,nnote,nreview) values %s;" % str(row))
            except Exception as err:
                print("Error '%s' : %s" % (row[1], str(err)))
        self.exec("""create table users (
            name text,
            password text,
            apikey text,
            data text
            ) """)
        self.conn.commit()


    def table_exists(self, name):
        if isinstance(name, (tuple, list)):
            for x in name:
                if not self.table_exists(x): return False
            return True
        else:
            return self.one("select count(name) from sqlite_master where type='table' AND name='%s'" % name) >0

    def init_user(self, username, file):
        with open(file) as f:
            js = json.loads(f.read())
            lists={}
            for row in js["db"]:
                row=js["db"][row]
                for ll in row["lists"]:
                    if not ll in lists:
                        lists[ll]=len(lists)


        usr=self.exec("select name from sqlite_master where type='table' AND name='%s'" % username)
        if not len(usr):
            self.exec("insert into users (name, password) values ('%s', '%s') " % (username, utils.password("")))
            query="""create table %s(
                filmid int,
                ownnote INT,
                tosee boolean,
                seen boolean,
                comment text,
                lists text,
                foreign key(filmid) references films(id)
            );
            """ % username
            ret=self.exec(query)
            self.conn.commit()

            done={}
            i=0
            for key in js["db"]:
                obj = js["db"][key]
                row = (int(key), obj["ownnote"], obj["tosee"], obj["seen"], obj["comment"], ",".join(obj["lists"]))


                query="insert into %s (filmid, ownnote, tosee, seen, comment, lists) values (%s,%s,%s,%s,%s,%s)" % (username,
                             key,
                             ("%.f" % obj["ownnote"]) if obj["ownnote"]!=None else "NULL",
                             "TRUE" if obj["tosee"] else "FALSE",
                             "TRUE" if obj["seen"] else "FALSE",
                             "'%s'" % (obj["comment"] if obj["comment"] else ''),
                             "'%s'" % ",".join(obj["lists"]))
                i+=1
                self.exec(query)
                done[int(key)]=True
            for row in self.exec("select * from films"):
                if not row[0] in done:
                    self.exec("insert into %s (filmid, ownnote, tosee, seen, comment, lists) values (%d, NULL, FALSE, FALSE, '', '')" %
                              (username, row[0]))
            self.conn.commit()

        usr = self.exec("select name from sqlite_master where type='table' AND name='%s_lists'" % username)
        if not len(usr):
            query = """create table %s_lists(
                                    id text,
                                    name text
                                );
                                """ % username
            ret = self.exec(query)
            for key in js["lists"]:
                val = js["lists"][key]
                query = "insert into %s_lists (id, name) values ('%s', '%s') " % (
                    username,
                    key,
                    val["name"]
                )
                self.conn.execute(query)
            self.conn.commit()

        usr = self.exec("select name from sqlite_master where type='table' AND name='%s_requests'" % username)
        if not len(usr):
            query = """create table %s_requests(
                                    name text,
                                    value text
                                );
                                """ % username
            ret = self.exec(query)
            for key in js["requests"]:
                query = "insert into %s_requests (name, value) values ('%s', '%s') " % (
                    username,
                    key,
                    json.dumps(js["requests"][key])
                )
                self.conn.execute(query)
            self.conn.commit()

    def commit(self):
        return self.conn.commit()

def create_datase(output, films, user):
    sql=SQConnector(output)
    sql.init_base(films)
    sql.init_user(user, "user/%s.json" % user)

if __name__ == "__main__":
    create_datase("db/new.db", "db.json", "fanch")
    """
    print("xxsx")
    sql=SQConnector("db/out.db")

    print(sql.one("select  count(*) from films;"))
    print(tuple(map(lambda x: x[0] ,sql.conn.execute("select * from films, fanch where id=filmid and id=123").description)))
    rs=sql.find("fanch", "'thriller' in genre")"""
 

