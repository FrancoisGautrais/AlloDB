import json

import config


def emptyrow():
    return {
        "ownnote": None,
        "tosee" : False,
        "seen" : False,
        "comment" : ""
    }

class User:
    HEADS=["ownnote", "tosee", "seen", "comment"]

    def __init__(self, name=None, js=None):
        self.db={}
        self.change=False
        if name:
            self.name=name
        elif js:
            self.name=js["name"]
            self.db=js["db"]

    def changed(self): return self.change

    def json(self):
        js={}
        js["name"]=self.name
        js["db"]=self.db
        return json.dumps(js)

    def array(self, id):
        out=[]
        if id in self.db:
            tmp=self.db[id]
            for h in User.HEADS:
                out.append(tmp[h])
        return out

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