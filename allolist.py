import uuid

import utils
from allodbrow import DbRow
from resultset import ResultSet

class AlloList:
    def __init__(self, js={}, name=""):
        self.id = js["id"] if js else utils.new_id()
        self.name= js["name"] if js else name
        self.list=js["list"] if js else []

    def result_set(self, db, order_type=[], order=[]):
        rs = ResultSet(db, order_type, order)
        for x in self.list:
            rs.put(db.ids[x])
        return rs.close()

    def remove(self, idfilm):
        self.list.remove(idfilm)

    def insert(self, i, id):
        if isinstance(id, DbRow): id=id.id
        if not id in self.list:
            self.list.insert(i, id)

    def swap(self, a, b):
        tmp=self.list[a]
        self.list[a]=self.list[b]
        self.list[b]=tmp

    def append(self, id):
        if isinstance(id, DbRow): id=id.id
        if not id in self.list:
            self.list.append(id)


    def up(self, id):
        if isinstance(id, DbRow): id=id.id
        try:
            i=self.list.index(id)
            if i>0: self.swap(i-1, i)
        except: pass

    def down(self, id):
        if isinstance(id, DbRow): id=id.id
        try:
            i=self.list.index(id)
            if i<len(self.list)-1: self.swap(i+1, i)
        except: pass


    def json(self):
        return {
            "id" : self.id,
            "list" : self.list,
            "name" : self.name
        }

    def json_set(self, db):
        x=self.result_set(db).moustache()
        x["name"]=self.name
        x["list-id"]=self.id
        return x

