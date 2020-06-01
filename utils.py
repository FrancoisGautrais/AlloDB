import random
import uuid
from urllib import parse
from http_server.utils import new_id
from hashlib import sha3_512
import base64

def dictassign(dest, *sources):
    for d in sources:
        for key in d:
            dest[key]=d[key]
    return dest

def dictcopy(*sources):
    return dictassign({}, *sources)


def urlencode(x):
    return parse.quote_plus(x)

def urldecode(x):
    return parse.quote_plus(x)



def password(pwd):
    x=sha3_512(pwd.encode()).digest()
    return base64.b64encode(x).decode("ascii")

def check_password(plain, encr):
    return password(plain)==encr

def new_key(size):
    out = ""
    chars = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_"
    for i in range(size):
        out += chars[random.randint(0, len(chars) - 1)]
    return out