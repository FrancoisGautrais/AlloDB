import json
import os

def tocsvval(val):
    out=""
    if isinstance(val,  str): val=[val]
    if isinstance(val, (int, float) ): out=str(val)
    if isinstance(val, list):
        out='"'
        for i in range(len(val)):
            out+=("," if i>0 else "")+val[i]
        out += '"'
    return out+";"

def urltoid(url):
    n=url.find("=")
    if n>=0:
        url=url[n+1]
        n=url.find(".")
        if n>=0:
            return int(url[n])
    return -1

def jstoperson(js):
    return js["name"]
    #out=str(urltoid(js["url"])) if "url" in js else "-1"
    #return out+":"+js["name"]

def jstoimage(js):
    return js["url"]

def jstoarraystr(js):
    if isinstance(js, str): return [js]
    return js

def jstoarrayperson(js):
    out=[]
    if isinstance(js, (list, tuple)) :
        for var in js:
            out.append(jstoperson(var))
        return out
    return jstoperson(js)

def jstoduration(js):
    h=js.find("H")
    return int(js[2:h])*60+int(js[h+1:h+3])

def jsval(js, *args):
    for arg in args:
        if arg in js: js=js[arg]
        else:
            return ""
    return js


def csv_head():
    return "id;name;image;genre;duration;description;director;actor;creator;music;note;nnote;nreview;trailer;\n"

def js_to_csv(js):
    out=""
    out+=tocsvval(jsval(js, "id")) #id
    out+=tocsvval(jsval(js, "name")) #name
    out+=tocsvval(jsval(js, "image"))  if "image" in js else ";" #image
    out+=tocsvval(jstoarraystr(jsval(js, "genre")))  if "genre" in js else ";"
    out+=tocsvval(jstoduration(jsval(js, "duration"))) if "duration" in js else ";"
    out+=tocsvval(jsval(js, "description"))  if "description" in js else ";"
    out+=tocsvval(jstoarrayperson(jsval(js, "director")))  if "director" in js else ";"
    out+=tocsvval(jstoarrayperson(jsval(js, "actor")))  if "actor" in js else ";"
    out+=tocsvval(jstoarrayperson(jsval(js, "creator"))) if "creator" in js else ";"
    out+=tocsvval(jstoarrayperson(jsval(js, "musicBy"))) if "musicBy" in js else ";"

    if "aggregateRating" in js:
        notes=js["aggregateRating"]
        out+=tocsvval(float(jsval(notes, "ratingValue").replace(",","."))) if "ratingValue" in notes else ";"
        out+=tocsvval(int(jsval(notes, "ratingCount"))) if "ratingCount" in notes else ";"
        out+=tocsvval(int(jsval(notes, "reviewCount"))) if "reviewCount" in notes else ";"
    else:
        out+=";;;"

    if "trailer" in js:
        t=js["trailer"]
        if isinstance(t, list): t=t[0]
        out+=tocsvval(js["trailer"]["url"])
    else:
        out+=";"
    return out+"\n"


def filetojson(filename):
    with open(filename) as f:
        return json.loads(f.read())

def dirtocsv(dir, out):
    with open(out, "w") as f:
        f.write(csv_head())
        for file in os.listdir(dir):
            if file.lower().endswith(".json"):
                f.write(js_to_csv(filetojson(os.path.join(dir, file))))



dirtocsv("/home/fanch/allocine/", "result.csv")