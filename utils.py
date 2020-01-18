import json
import os
def jsonfromfile(f):
    with open(f, "r") as f:
        return json.loads(f.read())
    return None


def obj_to_arr(js, columns):
    arr=[]
    for x in columns:
        if isinstance(x, str): x=(x, None, None)
        if len(x) == 1: x=(x[0], None, None)
        if len(x) == 2: x=(x[0], x[1], None)
        v=jsval(js, *x[:3])
        print(v)
        arr.append(v)


def _jsvalarray(js, path, fct, default):
    out=[]
    i = 0
    while i < len(path):
        x = path[i]
        if x == "*":
            if not isinstance(js, (list, tuple)): js=[js]
            i += 1
            for y in js:
                out.append(_jsval(y, path[i:], fct, default))
        elif js and isinstance(js, object) and x in js:
            js = js[x]
        else:
            return default
        i += 1
    return out

def _jsvalcommon(js, path, fct, default):
    for x in path:
        if js and isinstance(js, object) and x in js:
            js=js[x]
        else: return default
    return js

def _jsval(js, path, fct, default):
    if "*" in path: return _jsvalarray(js, path, fct, default)
    return _jsvalcommon(js, path, fct, default)


def jsval(js, path, fct=None, default=None):
    if isinstance(path, str): path=path.split("/")
    out=_jsval(js, path, fct, default)
    if fct and out: out=fct(out)
    return out


def castarr(x):
    if not isinstance(x, list): return [x]
    return x

def floatvirg(x):
    return float(x.replace(",", "."))

def test(start, end):
    for i in range(start, end):
        path="/home/fanch/allocine/"+str(i)+".json"
        if os.path.isfile(path):
            obj_to_arr(jsonfromfile(path),
                       [
                            ("id", None, None, "id"),
                            ("name", None, None, "name"),
                            ("image/url", None, None, "image"),
                           ("pays/*", castarr, None, "nationality"),
                           ("annee",  None, None, "year"),
                           ("genre/*", castarr, None, "genre"),
                           ("description",  None, None, "description"),
                           ("director/*/name", None, None, "director"),
                           ("actor/*/name", castarr, None, "actor"),
                           ("creator/*/name", castarr, None, "creator"),
                           ("musicBy/*/name", castarr, None, "musicBy"),
                           ("aggregateRating/ratingValue", floatvirg, None, "note"),
                           ("aggregateRating/ratingCount", int, None, "nnote"),
                           ("aggregateRating/reviewCount", int, None, "nreview")


                       ])
test(2,20)