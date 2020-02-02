from allodb import ResultSet, DbRow
class AlloList:
    def __init__(self, js={}, name=""):
        self.name= js["name"] if js else name
        self.list=js["list"] if js else []

    def insert(self, i, id):
        if isinstance(id, DbRow): id=id.id
        if not id in self.list:
            self.list.insert(i, id)

    def swap(self, a, b):
        tmp=self.list

    def append(self, id):
        if isinstance(id, DbRow): id=id.id
        self.list.append(id)

    def up(self, id):
        if isinstance(id, DbRow): id=id.id
        try:
            i=self.list.index(id)
            if i>0: pass #==================================
        except: pass #==================================

