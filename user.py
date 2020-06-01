import json
import utils

class User:
    HEADS=["ownnote", "tosee", "seen", "comment", "lists"]

    def __init__(self, conn):
        self.conn=conn
        self.name=""
        self.oldname=""
        self.password=""
        self.api=""
        self.request={}
        self.data={}

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

