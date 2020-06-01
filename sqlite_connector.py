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

    def init_base(self, file):
        with open(file, "r") as f:
            js=json.loads(f.read())
        self.exec("""create table films (
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
""")
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
 

