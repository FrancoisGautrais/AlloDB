import json
import utils


class BadUserException(Exception):
    pass


class ImportException(Exception):
    pass


class User:
    HEADS=["ownnote", "tosee", "seen", "comment", "lists"]
    ACTION_NEW="new"
    ACTION_IMPORT="import"
    ACTION_REPLACE="replace"
    def __init__(self, conn):
        self.conn=conn
        self.name=""
        self.oldname=""
        self.password=""
        self.api=""
        self.request={}
        self.data={}
        self.request=None

    def set_password(self, password):
        self.password=utils.password(password)
        self.conn.exec("update users set password='%s' where name='%s' " % (self.password, self.name))
        self.conn.commit()

    def new_api(self):
        self.api = utils.new_key(64)
        self.conn.exec("update users set apikey='%s' where name='%s' " % (self.api, self.name))
        self.conn.commit()

    @staticmethod
    def load(conn, name):
        if isinstance(name, str):
            row=conn.onerow("select * from users where name='%s' " % name)
        else:
            row=name
        x=User(conn)
        x.name=row[0]
        x.oldname=row[0]
        x.password=row[1]
        x.api=row[2]
        x.data=json.loads(row[3]) if row[2] else {}
        return x

    def save(self):
        self.conn.exec("update users set name='%s', password='%s', apikey='%s', data='%s' where name='%s' "% (
            self.name, self.password, self.api, json.dumps(self.data), self.oldname
        ))
        self.conn.commit()
        self.oldname=self.name

    @staticmethod
    def row_to_json(row):
        return {
            "ownnote" : row[1] if row[1] else None,
            "tosee" : True if row[2] else False,
            "seen" : True if row[3] else False,
            "comment" : row[4] if row[4] else None,
            "lists" : row[5].split(",") if row[5] else []
        }

    def export(self):
        films=self.conn.exec("select * from %s where seen or tosee or comment or ownnote or lists" % self.name)
        db={}
        listsdb={}
        for row in films:
            obj=User.row_to_json(row)
            db[str(row[0])]=obj
            for x in obj["lists"]:
                if not x in listsdb:
                    listsdb[x]={
                        "id" : x,
                        "lists" : [],
                        "name" : self.conn.one("select name from %s_lists where id='%s'" %( self.name, x))
                    }
                listsdb[x]["lists"].append(str(row[0]))
        req=self.conn.exec("select * from %s_requests" % self.name)
        requestdb={}
        for r in req:
            requestdb[r[0]]=json.loads(r[1])

        return {
            "name" : self.name,
            "db" : db,
            "requests" : requestdb,
            "lists" : listsdb
        }


    def replace_from_js(self, js):
        if js["name"]!=self.name:
            raise BadUserException("utilisateur attendu '%s', trouvé '%s'" % (
                self.name, js["name"]
            ))
        n=self.conn.one("select count(*) from %s where ownnote or tosee or seen or comment or lists"%self.name)
        if n>len(js["db"]):
            raise ImportException("Le nouveau fichier contient moins de donné qu'actuellement")
        self.conn.exec("drop table %s " % self.name)
        self.conn.exec("drop table %s_requests " % self.name)
        self.conn.exec("drop table %s_lists " % self.name)
        User.import_user(self.conn, js)
        

    @staticmethod
    def new_from_file(conn, file):
        js=None
        with open(file) as f:
            js=json.loads(f.read())
        return User.import_user(conn, js)

    @staticmethod
    def import_user(conn, js):
        username=js["name"]
        lists={}
        for row in js["db"]:
            row=js["db"][row]
            for ll in row["lists"]:
                if not ll in lists:
                    lists[ll]=len(lists)


        usr=conn.exec("select name from sqlite_master where type='table' AND name='%s'" % username)
        if not len(usr):
            conn.exec("insert into users (name, password) values ('%s', '%s') " % (username, utils.password("")))
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
            ret=conn.exec(query)
            conn.commit()

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
                conn.exec(query)
                done[int(key)]=True
            for row in conn.exec("select * from films"):
                if not row[0] in done:
                    conn.exec("insert into %s (filmid, ownnote, tosee, seen, comment, lists) values (%d, NULL, FALSE, FALSE, '', '')" %
                              (username, row[0]))
            conn.commit()

        usr = conn.exec("select name from sqlite_master where type='table' AND name='%s_lists'" % username)
        if not len(usr):
            query = """create table %s_lists(
                                    id text,
                                    name text
                                );
                                """ % username
            ret = conn.exec(query)
            for key in js["lists"]:
                val = js["lists"][key]
                query = "insert into %s_lists (id, name) values ('%s', '%s') " % (
                    username,
                    key,
                    val["name"]
                )
                conn.conn.execute(query)
            conn.conn.commit()

        usr = conn.exec("select name from sqlite_master where type='table' AND name='%s_requests'" % username)
        if not len(usr):
            query = """create table %s_requests(
                                    name text,
                                    value text
                                );
                                """ % username
            ret = conn.exec(query)
            for key in js["requests"]:
                query = "insert into %s_requests (name, value) values ('%s', '%s') " % (
                    username,
                    key,
                    json.dumps(js["requests"][key])
                )
                conn.conn.execute(query)
            conn.conn.commit()

        return User.load(conn, username)




