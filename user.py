import json
from allolist import AlloList
import config


def emptyrow():
    return {
        "ownnote": None,
        "tosee" : False,
        "seen" : False,
        "comment" : "",
        "lists" : []
    }

class User:
    HEADS=["ownnote", "tosee", "seen", "comment", "lists"]

    def __init__(self, name=None, js=None):
        self.db={}
        self.change=False
        self.lists={}
        self.requests={}
        if name:
            self.name=name
        elif js:
            self.name=js["name"]
            self.db=js["db"]
            for x in self.db:
                row=self.db[x]
                if "lists" in row and "d5533acd" in row["lists"]:
                    print("--------- here ---------")
                    row["lists"].remove("d5533acd")
            if "lists" in js:
                for x in js["lists"]:
                    self.lists[x]=AlloList(js=js["lists"][x])
            else: js["lists"]=[]

            if "requests" in js:
                self.requests=js["requests"]
            #self.remove_to_list(None, "7ac51d11")
            for x in self.db:
                if (not "lists" in self.db[x] or self.db[x]["lists"]==None):
                    self.db[x]["lists"]=[]
            self.save()

    def changed(self): return self.change

    def list_json(self):
        all={}
        for x in self.lists:
            all[x]=self.lists[x].json()
        return all

    def import_json(self, js):
        for x in js:
            self.db[x]=js[x]
        self.save()

    def json(self):
        js={}
        js["name"]=self.name
        js["db"]=self.db
        js["requests"]=self.requests
        x={}
        for l in self.lists:
            x[l]=self.lists[l].json()
        js["lists"]=x
        return json.dumps(js)


    def array(self, id):
        out=[]
        if id in self.db:
            tmp=self.db[id]
            for h in User.HEADS:
                out.append(tmp[h])
        return out

    def list_get_by_id(self, id):
        if id in self.lists: return self.lists[id]
        return None

    def list_remove(self, id):
        if id in self.lists:
            for fid in self.lists[id].list.copy():
                self.remove_to_list(fid, id)
            del self.lists[id]

    def put(self, id, array):
        if len(array) != len(User.HEADS): raise Exception("Error bad sie of array to put")
        obj={}
        for i in range(len(array)):
            obj[User.HEADS[i]]=array[i]
        self.db[id]=obj

    def heads(self):
        return User.HEADS

    def __getitem__(self, item):
        if not (item in self.db): self.db[item]=emptyrow()
        return self.db[item]

    def resolve(self, id, item):
        if isinstance(id, int): id=str(id)
        if id in self.db and item in self.db[id]:
            return self.db[id][item]
        return None

    def set(self, id, k, v):
        if not (id in self.db): self.db[id]=emptyrow()
        if k in self.db[id]:
            self.db[id][k] = v
            self.save()
        else: raise Exception(k+" not a user header")

    def add_to_list(self, filmid, listid):
        if not listid in self.lists: return False
        if not (filmid in self.db): self.db[filmid]=emptyrow()
        if not "lists" in self.db[filmid]: self.db[filmid]["lists"]=[]
        self.db[filmid]["lists"].append(listid)
        self.lists[listid].list.append(filmid)
        return True

    def add_request(self, name, req):
        self.requests[name]=req

    def delete_request(self, name):
        del self.requests[name]

    def remove_to_list(self, filmid, listid):
        self.lists[listid].list.remove(filmid)
        self.db[filmid]["lists"].remove(listid)
        return True

    def save(self):
        userpath=config.user(self.name)
        with open(userpath, "w") as f:
            f.write(self.json())
            self.change=False

    @staticmethod
    def createuser(name): return User(name=name)

    @staticmethod
    def fromjson(js): return User(js=js)


    @staticmethod
    def fromjsonfile(file):
        file = config.user(file)
        with open(file) as f:
            usr = User(js=json.loads(f.read()))
        return usr