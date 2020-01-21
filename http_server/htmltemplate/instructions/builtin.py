from ...filecache import filecache
from ..htmlgen import html_gen_fd
import  copy
import json
def inst_include(args, data):
    x=copy.deepcopy(data)
    with filecache.open(args[0]) as f:
        if len(args)>1:
            x.update(args[1])
        return html_gen_fd(f, x)

def inst_get(args, data):
    acc=data
    for x in args:
        acc=acc[x]
    return acc
#
# set(k ,k2, .., kn, value)
#
def inst_set(args, data):
    inst_get(args[:-2], data)[args[-2]]=args[-1]

def inst_cat(args, data):
    acc=""
    for x in args:
        acc+=str(x)
    return  acc

def inst_kv(args, data):
    return (args[0], args[1])

def inst_list(args, data):
    return args

def inst_objl(args, data):
    out={}
    i=0
    while i+1<len(args):
        out[args[i]]=args[i+1]
        i+=2
    return out


def inst_None(args, data): return None

def inst_true(args, data): return True

def inst_false(args, data): return False

def inst_bloc(args, data):
    return args[-1]

def inst_object(args, data):
    obj={}
    for x in args:
        obj[x[0]]=x[1]
    return obj


def inst_if(args, data):
    x = args[0]
    if x: return args[1]
    elif len(args)>2: return args[2]
    return ""

def inst_not(args, data):
    return not args[0]

def inst_eq(args, data): return not args[0] == args[1]
def inst_diff(args, data): return not args[0] != args[1]
def inst_inf(args, data): return not args[0] < args[1]
def inst_infeq(args, data): return not args[0] <= args[1]
def inst_sup(args, data): return not args[0] > args[1]
def inst_supeq(args, data): return not args[0] >= args[1]


def inst_mobile(args, data):
    x = data["user"]["mobile"]
    if x:
        return args[0]
    elif len(args) > 1:
        return args[1]

def inst_desktop(args, data):
    x = not data["user"]["mobile"]
    if x:
        return args[0]
    elif len(args) > 1:
        return args[1]

def inst_json(args, data):
    return json.dumps(args[0])
