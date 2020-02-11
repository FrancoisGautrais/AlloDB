import uuid
from urllib import parse
from http_server.utils import new_id

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