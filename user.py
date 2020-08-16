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
        self.permission=""
        self.request=None

    def set_password(self, password):
        self.password=utils.password(password)
        self.conn.exec("update users set password='%s' where name='%s' " % (self.password, self.name))
        self.conn.commit()

    def set_perm(self, p, val):
        if val:
            if not p in self.permission:
                self.permission+=p
            else: return
        else:
            if p in self.permission:
                tmp=""
                for c in self.permission:
                    if c!=p:
                        tmp+=p
                self.permission=tmp
            else:
                return
        self.conn.exec("update users set permission='%s' where name='%s' " % (self.permission, self.name))
        self.conn.commit()

    def has_perm(self, p : str):
        if len(p)>1: return False
        return p in self.permission

    def is_admin(self): return self.has_perm("a")

    def set_admin(self, val): self.set_perm("a", val)


    def new_api(self):
        self.api = utils.new_key(64)
        self.conn.exec("update users set apikey='%s' where name='%s' " % (self.api, self.name))
        self.conn.commit()
        return self.api

    @staticmethod
    def default_user_data(data):
        tmp = {
            "default_search" : None
        }
        for key in data:
            tmp[key]=data[key]
        return tmp

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
        x.data=User.default_user_data(json.loads(row[3]) if row[3] else {})
        x.permission=row[4] if row[4] else ""
        return x

    def save(self):
        self.conn.exec("update users set name='%s', password='%s', apikey='%s', data='%s' permission='%s' where name='%s' "% (
            self.name, self.password, self.api, json.dumps(self.data), self.permission, self.oldname
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
    def create_user(conn, js):
        """
        js: {
            name: name,
            password: password,
            admin: admin (False)
        }
        :param conn:
        :param js:
        :return:
        """
        return User.import_user(conn,
                                {"name" : js["name"]},
                                password=js["password"],
                                isadmin=js["admin"] if js["admin"] else False)

    @staticmethod
    def delete_user(conn, name):
        conn.exec("delete from users where name='%s' " % name)
        conn.exec("drop table %s_lists " % name)
        conn.exec("drop table %s_requests " % name)
        conn.exec("drop table %s " % name)
        conn.commit()


    @staticmethod
    def import_user(conn, js, password="", isadmin=False):
        username=js["name"]
        lists={}
        if "db" in js:
            for row in js["db"]:
                row=js["db"][row]
                for ll in row["lists"]:
                    if not ll in lists:
                        lists[ll]=len(lists)

        perm="a" if isadmin else ""
        usr=conn.exec("select name from sqlite_master where type='table' AND name='%s'" % username)
        if not len(usr):
            conn.exec("insert into users (name, password, permission) values ('%s', '%s', '%s') " % (username, utils.password(password), perm))
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
            if "db" in js:
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
            if "lists" in js:
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
            if "requests" in js:
                for key in js["requests"]:
                    query = "insert into %s_requests (name, value) values ('%s', '%s') " % (
                        username,
                        key,
                        json.dumps(js["requests"][key])
                    )
                    conn.conn.execute(query)
            conn.conn.commit()

        return User.load(conn, username)




