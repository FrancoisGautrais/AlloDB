import json
import alloimport
import time
import uuid
from functools import cmp_to_key
import random
import utils


def sortkey(a, b, key, coef):
    a = a[key]
    b = b[key]
    if a != None and b != None:
        if isinstance(a, str):
            a = a.lower()
            b = b.lower()
        if a == b: return 0
        try:
            return -1 * coef if (a < b) else 1 * coef
        except:
            y=1
    if a:
        return 1 * coef
    elif b:
        return -1 * coef
    return 0


class ResultSet:

    def __init__(self, db, col=[], order=[], set=None, pagesize=-1, page=0):
        self.db=db
        self.id=utils.new_id()
        self.start_time=time.time()
        self.process_time=0
        self.order=order
        self.columns=col
        self.pagesize=pagesize
        self.page=page
        self.data= (set if set else [])
        if set!=None: self.close()

    def moustache(self, base={}):
        arr=[]
        for x in self.data:
            arr.append(x.json(self.columns))

        return utils.dictassign({
            "count" : len(self.data),
            "time" : int(self.process_time*1000)/1000,
            "data" : arr if self.pagesize<=0 else arr[self.page*self.pagesize:(self.page+1)*self.pagesize],
            "page" : self.page,
            "nperpage" : self.pagesize,
            "id" : self.id,
            "npages" : 1 if self.pagesize<=0 else (int(len(self.data)/self.pagesize)+ (1 if len(self.data)%self.pagesize>0 else 0)),
            "payslist": alloimport.ID_TO_PAYS
        }, base)

    def close(self):
        if self.order and len(self.order)>0:
            key, sens = self.order[0]
            self.data = sorted(self.data, key=cmp_to_key(lambda a, b: sortkey(a, b, key, 1 if sens else -1)))
        self.process_time = time.time() - self.start_time
        return self


    def sort(self, key, reverse):
        if key=="shuffle":
            random.shuffle(self.data)
        else:
            self.data = sorted(self.data, key=cmp_to_key(lambda a, b: sortkey(a, b, key, 1 if reverse else -1)))

    def put(self, row):
        if isinstance(row, (list, tuple)):
            self.data+=row
        else:
            self.data.append(row)

    def row_at(self, n):
        return self.data[n]

    def __len__(self): return len(self.data)

    def __repr__(self):
        return self.__str__()

    def __str__(self):
        head=self.db.header.allheader
        out=str(len(self.data))+" résultats; en "+str( int(self.process_time*1000000)/1000)+" ms\n"
        out+=str(self.db.header.format(head))+"\n"
        for x in self.data:
            out+=x.format(head)+"\n"
        return out