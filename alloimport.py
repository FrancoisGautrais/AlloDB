import json
import os
import ast

import requests


def filter_nat(line):
    n=line.find('nationality"> ')
    if n>0:
        line=line[n+14:]
        nn=line.find("<")
        return line[:nn]
    return None

def filter_id(line):
    n=line.find('"movie_id":"')
    if n>0:
        line=line[n+12:]
        n=line.find('"')
        return line[:n]
    return None

def filter_date(line):
    n=line.find('/annee-')
    if n>0:
        line=line[n+7:]
        nn=line.find("/")
        return int(line[:nn])
    n=line.find("production_year=")
    if n>0:
        line=line[n+16:]
        return int(line[:line.find('"')])
    return None

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
        arr.append(v)
    return arr


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

def castduration(js):
    h=js.find("H")
    return int(js[2:h])*60+int(js[h+1:h+3])

def castarr(x):
    if not isinstance(x, list): return [x]
    return x

def floatvirg(x):
    return float(x.replace(",", "."))

def castpays(x):
    out=[]
    if x:
        for k in x:
            out.append(PAYS_LIST[k])
    return out


def extract(htmlcont, columns):
    content = htmlcont
    n = content.find('<script type="application/ld+json">')
    js = {}
    if n >= 0:
        content = content[n + 36:].replace("\r", "").replace("\n", "").replace("\t", "")
        n = content.find('</script>')
        if n >= 0:
            content = content[:n]
            js = json.loads(content)

    js["pays"] = []
    js["annee"] = None
    for line in htmlcont.split("\n"):
        x = filter_nat(line)
        if x: js["pays"].append(x)
        x = filter_date(line)
        if x: js["annee"] = x
        x = filter_id(line)
        if x: js["id"] = x
    x=obj_to_arr(js, columns)
    return x


GENRE_LIST={
    "inconnu" : "",
    "" : "inconnu",
    "comédie" : "comédie",
    "divers" : "divers",
    "drame" : "drame",
    "documentaire" : "documentaire",
    "romance" : "romance",
    "comédie dramatique" : "comédie dramatique",
    "epouvante-horreur" : "epouvante-horreur",
    "thriller" : "thriller",
    "animation" : "animation",
    "espionnage" : "espionnage",
    "action" : "action",
    "famille" : "famille",
    "policier" : "policier",
    "guerre" : "guerre",
    "erotique" : "erotique",
    "historique" : "historique",
    "western" : "western",
    "aventure" : "aventure",
    "fantastique" : "fantastique",
    "musical" : "musical",
    "bollywood" : "bollywood",
    "arts martiaux" : "arts martiaux",
    "comédie musicale" : "comédie musicale",
    "expérimental" : "expérimental",
    "science fiction" : "science fiction",
    "biopic" : "biopic",
    "sport event" : "sport event",
    "péplum" : "péplum",
    "judiciaire" : "judiciaire",
    "show" : "show",
    "opera" : "opera",
    "concert" : "concert",
    "survival, science-fiction, aventure" : "survival",
    "classique" : "classique"
}

PAYS_LIST={
    "inconnu" : "",
    "" : "inconnu",
    "af": "afghan",
    "afghan": "af",
    "al": "albanais",
    "albanais": "al",
    "dz": "algérien",
    "algérien": "dz",
    "de": "ouest-allemand",
    "allemand": "de",
    "us": "U.S.A.",
    "américain": "us",
    "ad": "andorran",
    "andorran": "ad",
    "ao": "angolais",
    "angolais": "ao",
    "ag": "antiguais",
    "antiguais": "ag",
    "ar": "argentin",
    "argentin": "ar",
    "am": "arménien",
    "arménien": "am",
    "au": "australien",
    "australien": "au",
    "at": "autrichien",
    "autrichien": "at",
    "az": "azerbaïdjanais",
    "azerbaïdjanais": "az",
    "bs": "bahaméen",
    "bahaméen": "bs",
    "bh": "bahreini",
    "bahreini": "bh",
    "bb": "barbadien",
    "barbadien": "bb",
    "be": "belge",
    "belge": "be",
    "bz": "belizien",
    "belizien": "bz",
    "": "équato-guinéen",
    "bengali": "",
    "bm": "Bermudien",
    "Bermudien": "bm",
    "bt": "bhoutanais",
    "bhoutanais": "bt",
    "birman": "",
    "bissau-guinéen": "",
    "biélorusse": "",
    "bo": "bolivien",
    "bolivien": "bo",
    "ba": "bosniaque",
    "bosniaque": "ba",
    "bw": "botswanais",
    "botswanais": "bw",
    "uk": "britannique",
    "britannique": "uk",
    "br": "brésilien",
    "brésilien": "br",
    "bg": "bulgare",
    "bulgare": "bg",
    "bf": "burkinabé",
    "burkinabé": "bf",
    "bi": "burundais",
    "burundais": "bi",
    "bj": "béninois",
    "béninois": "bj",
    "kh": "cambodgien",
    "cambodgien": "kh",
    "cm": "camerounais",
    "camerounais": "cm",
    "ca": "Québecois",
    "canadien": "ca",
    "cap-verdiens": "",
    "cf": "centrafricain",
    "centrafricain": "cf",
    "cl": "chilien",
    "chilien": "cl",
    "cn": "chinois",
    "chinois": "cn",
    "cy": "chypriote",
    "chypriote": "cy",
    "co": "colombien",
    "colombien": "co",
    "cg": "congolais",
    "congolais": "cg",
    "kr": "sud-coréen",
    "coréen": "kr",
    "cr": "Costaricain",
    "Costaricain": "cr",
    "hr": "croate",
    "croate": "hr",
    "cu": "cubain",
    "cubain": "cu",
    "dk": "danois",
    "danois": "dk",
    "dj": "djiboutiens",
    "djiboutiens": "dj",
    "dm": "dominicain",
    "dominicain": "dm",
    "es": "espagnol",
    "espagnol": "es",
    "est-allemand": "de",
    "ee": "estonien",
    "estonien": "ee",
    "fi": "finlandais",
    "finlandais": "fi",
    "fr": "français",
    "français": "fr",
    "ga": "gabonais",
    "gabonais": "ga",
    "gh": "ghanéen",
    "ghanéen": "gh",
    "gr": "grec",
    "grec": "gr",
    "gt": "guatémaltèque",
    "guatémaltèque": "gt",
    "gn": "guinéen",
    "guinéen": "gn",
    "ge": "géorgien",
    "géorgien": "ge",
    "ht": "haïtien",
    "haïtien": "ht",
    "hn": "hondurien",
    "hondurien": "hn",
    "hk": "hong-kongais",
    "hong-kongais": "hk",
    "hu": "hongrois",
    "hongrois": "hu",
    "in": "indien",
    "indien": "in",
    "id": "indonésien",
    "indonésien": "id",
    "Indéfini": "",
    "iq": "Irakien",
    "Irakien": "iq",
    "ir": "iranien",
    "iranien": "ir",
    "ie": "irlandais",
    "irlandais": "ie",
    "is": "islandais",
    "islandais": "is",
    "il": "israélien",
    "israélien": "il",
    "it": "italien",
    "italien": "it",
    "ci": "ivoirien",
    "ivoirien": "ci",
    "jm": "jamaïcain",
    "jamaïcain": "jm",
    "jp": "japonais",
    "japonais": "jp",
    "jo": "jordanien",
    "jordanien": "jo",
    "kz": "kazakh",
    "kazakh": "kz",
    "ke": "Kenyan",
    "Kenyan": "ke",
    "kg": "kirghiz",
    "kirghiz": "kg",
    "kw": "kowetien",
    "kowetien": "kw",
    "la": "laotien",
    "laotien": "la",
    "lv": "letton",
    "letton": "lv",
    "lb": "libanais",
    "libanais": "lb",
    "ly": "libyen",
    "libyen": "ly",
    "lr": "libérien",
    "libérien": "lr",
    "li": "liechtensteinois",
    "liechtensteinois": "li",
    "lt": "lituanien",
    "lituanien": "lt",
    "lu": "luxembourgeois",
    "luxembourgeois": "lu",
    "mk": "macédonien",
    "macédonien": "mk",
    "my": "malaisien",
    "malaisien": "my",
    "mw": "malawites",
    "malawites": "mw",
    "mg": "malgache",
    "malgache": "mg",
    "ml": "malien",
    "malien": "ml",
    "mt": "maltais",
    "maltais": "mt",
    "ma": "marocain",
    "marocain": "ma",
    "mu": "mauriciens",
    "mauriciens": "mu",
    "mr": "mauritanien",
    "mauritanien": "mr",
    "mx": "mexicain",
    "mexicain": "mx",
    "md": "moldave",
    "moldave": "md",
    "mc": "Monegasque",
    "Monegasque": "mc",
    "mn": "mongol",
    "mongol": "mn",
    "me": "monténégrin",
    "monténégrin": "me",
    "mz": "mozambiquais",
    "mozambiquais": "mz",
    "na": "namibien",
    "namibien": "na",
    "ni-vanuatu": "",
    "ni": "nicaraguéen",
    "nicaraguéen": "ni",
    "ne": "nigérian",
    "nigérian": "ne",
    "ng": "nigérien",
    "nigérien": "ng",
    "kp": "nord-coréen",
    "nord-coréen": "kp",
    "no": "norvégien",
    "norvégien": "no",
    "nl": "néerlandais",
    "néerlandais": "nl",
    "nz": "néo-zélandais",
    "néo-zélandais": "nz",
    "np": "népalais",
    "népalais": "np",
    "ouest-allemand": "de",
    "ug": "ougandais",
    "ougandais": "ug",
    "uz": "ouzbek",
    "ouzbek": "uz",
    "pk": "pakistanais",
    "pakistanais": "pk",
    "ps": "palestinien",
    "palestinien": "ps",
    "pa": "panaméen",
    "panaméen": "pa",
    "pg": "papouan-néo guinéen",
    "papouan-néo guinéen": "pg",
    "py": "paraguayen",
    "paraguayen": "py",
    "ph": "philippin",
    "philippin": "ph",
    "pl": "polonais",
    "polonais": "pl",
    "pr": "portoricain",
    "portoricain": "pr",
    "pt": "portugais",
    "portugais": "pt",
    "pe": "péruvien",
    "péruvien": "pe",
    "qa": "qatarien",
    "qatarien": "qa",
    "Québecois": "ca",
    "ro": "roumain",
    "roumain": "ro",
    "ru": "russe",
    "russe": "ru",
    "rw": "rwandais",
    "rwandais": "rw",
    "samoan": "us",
    "sa": "saoudien",
    "saoudien": "sa",
    "rs": "serbe",
    "serbe": "rs",
    "sl": "sierra-léonais",
    "sierra-léonais": "sl",
    "sg": "singapourien",
    "singapourien": "sg",
    "sk": "slovaque",
    "slovaque": "sk",
    "si": "slovène",
    "slovène": "si",
    "so": "somalien",
    "somalien": "so",
    "sd": "soudanais",
    "soudanais": "sd",
    "su": "soviétique",
    "soviétique": "su",
    "lk": "sri-lankais",
    "sri-lankais": "lk",
    "za": "sud-africain",
    "sud-africain": "za",
    "sud-coréen": "kr",
    "ch": "suisse",
    "suisse": "ch",
    "sr": "surinamien",
    "surinamien": "sr",
    "se": "suédois",
    "suédois": "se",
    "sz": "swazi",
    "swazi": "sz",
    "sy": "syrien",
    "syrien": "sy",
    "sn": "sénégalais",
    "sénégalais": "sn",
    "tj": "tadjik",
    "tadjik": "tj",
    "tz": "tanzanien",
    "tanzanien": "tz",
    "tw": "taïwanais",
    "taïwanais": "tw",
    "td": "tchadien",
    "tchadien": "td",
    "cz": "tchécoslovaque",
    "tchèque": "cz",
    "tchécoslovaque": "cz",
    "th": "thaïlandais",
    "thaïlandais": "th",
    "tg": "togolais",
    "togolais": "tg",
    "to": "tongien",
    "tongien": "to",
    "tt": "trinidadiens",
    "trinidadiens": "tt",
    "tn": "tunisien",
    "tunisien": "tn",
    "tr": "turc",
    "turc": "tr",
    "tm": "turkmène",
    "turkmène": "tm",
    "tuvaluan": "",
    "U.S.A.": "us",
    "ua": "ukrainien",
    "ukrainien": "ua",
    "uy": "uruguayen",
    "uruguayen": "uy",
    "vn": "vietnamien",
    "vietnamien": "vn",
    "ve": "vénézuélien",
    "vénézuélien": "ve",
    "yu": "yougoslave",
    "yougoslave": "yu",
    "ye": "yéménite",
    "yéménite": "ye",
    "zm": "zambien",
    "zambien": "zm",
    "zaïrois": "",
    "zimbabwéen": "",
    "eg": "égyptien",
    "égyptien": "eg",
    "émirati": "",
    "équato-guinéen": "",
    "ec": "équatorien",
    "équatorien": "ec",
    "et": "éthiopien",
    "éthiopien": "et"
}

ID_TO_PAYS={}
PAYS_TO_ID={}
for x in PAYS_LIST:
    if len(x)<=2:
        ID_TO_PAYS[x]=PAYS_LIST[x]
        PAYS_TO_ID[PAYS_LIST[x]]=x
