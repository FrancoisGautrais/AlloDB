import time
import json
import sqlite3
import resultset

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
        print(sql)
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
        print(query)
        cur.execute(query)
        rs.set_results(cur)
        return rs

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
                done[int(key)]=True
                print(i, query)
                print(i, self.exec(query))
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
                print(query)
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
                print(query)
                self.conn.execute(query)
            self.conn.commit()




"""
sql=SQConnector("db/tmp.db")

print(sql.one("select  count(*) from films;"))
print(tuple(map(lambda x: x[0] ,sql.conn.execute("select * from films, fanch where id=filmid and id=123").description)))
rs=sql.find("fanch", "'thriller' in genre")
 
"""
