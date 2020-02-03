import uuid
from urllib import parse

def new_id():
    return str(uuid.uuid4())[:8]

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