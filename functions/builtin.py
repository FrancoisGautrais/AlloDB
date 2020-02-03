from alloexpr import *
import random
from resultset import ResultSet
def fct_range(db, row , args):
    return Range(args[0].val(row), args[1].val(row))

def fct_count(db, row, args):
    x=db.match(args[0])
    return len(x)

def fct_rand(db, row, args):
    ndb=db.match(args[0])
    n=1
    if len(args)>1: n = args[1].val(row)
    out=ResultSet(db)
    found={}
    for i in range(min(n,len(ndb))):
        x=random.randint(0,len(ndb))
        while x in found: random.randint(0,len(ndb))
        found[x]=True
        out.put(ndb.row_at(x))

    return out.close()

