import json
import os
import sys
import time
import traceback
from functools import cmp_to_key

import allofunction
import user
import alloexpr
import requests

import utils
from alloexpr import Expr
from allolexer import Lexer
from io import StringIO

from alloparser import Parser

genrelist={
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

payslist={
    'afghan' : "af",
    'albanais' : "al",
    'algérien' : "dz",
    'allemand' : "de",
    'américain' : "us",
    'andorran' : "ad",
    'angolais' : "ao",
    'antiguais' : "ag",
    'argentin' : "ar",
    'arménien' : "am",
    'australien' : "au",
    'autrichien' : "at",
    'azerbaïdjanais' : "az",
    'bahaméen' : "bs",
    'bahreini' : "bh",
    'barbadien' : "bb",
    'belge' : "be",
    'belizien' : "bz",
    'bengali' : "",
    'Bermudien' : "bm",
    'bhoutanais' : "bt",
    'birman' : "",
    'bissau-guinéen' : "",
    'biélorusse' : "",
    'bolivien' : "bo",
    'bosniaque' : "ba",
    'botswanais' : "bw",
    'britannique' : "uk",
    'brésilien' : "br",
    'bulgare' : "bg",
    'burkinabé' : "bf",
    'burundais' : "bi",
    'béninois' : "bj",
    'cambodgien' : "kh",
    'camerounais' : "cm",
    'canadien' : "ca",
    'cap-verdiens' : "",
    'centrafricain' : "cf",
    'chilien' : "cl",
    'chinois' : "cn",
    'chypriote' : "cy",
    'colombien' : "co",
    'congolais' : "cg",
    'coréen' : "kr",
    'Costaricain' : "cr",
    'croate' : "hr",
    'cubain' : "cu",
    'danois' : "dk",
    'djiboutiens' : "dj",
    'dominicain' : "dm",
    'espagnol' : "es",
    'est-allemand' : "de",
    'estonien' : "ee",
    'finlandais' : "fi",
    'français' : "fr",
    'gabonais' : "ga",
    'ghanéen' : "gh",
    'grec' : "gr",
    'guatémaltèque' : "gt",
    'guinéen' : "gn",
    'géorgien' : "ge",
    'haïtien' : "ht",
    'hondurien' : "hn",
    'hong-kongais' : "hk",
    'hongrois' : "hu",
    'indien' : "in",
    'indonésien' : "id",
    'Indéfini' : "",
    'Irakien' : "iq",
    'iranien' : "ir",
    'irlandais' : "ie",
    'islandais' : "is",
    'israélien' : "il",
    'italien' : "it",
    'ivoirien' : "ci",
    'jamaïcain' : "jm",
    'japonais' : "jp",
    'jordanien' : "jo",
    'kazakh' : "kz",
    'Kenyan' : "ke",
    'kirghiz' : "kg",
    'kowetien' : "kw",
    'laotien' : "la",
    'letton' : "lv",
    'libanais' : "lb",
    'libyen' : "ly",
    'libérien' : "lr",
    'liechtensteinois' : "li",
    'lituanien' : "lt",
    'luxembourgeois' : "lu",
    'macédonien' : "mk",
    'malaisien' : "my",
    'malawites' : "mw",
    'malgache' : "mg",
    'malien' : "ml",
    'maltais' : "mt",
    'marocain' : "ma",
    'mauriciens' : "mu",
    'mauritanien' : "mr",
    'mexicain' : "mx",
    'moldave' : "md",
    'Monegasque' : "mc",
    'mongol' : "mn",
    'monténégrin' : "me",
    'mozambiquais' : "mz",
    'namibien' : "na",
    'ni-vanuatu' : "",
    'nicaraguéen' : "ni",
    'nigérian' : "ne",
    'nigérien' : "ng",
    'nord-coréen' : "kp",
    'norvégien' : "no",
    'néerlandais' : "nl",
    'néo-zélandais' : "nz",
    'népalais' : "np",
    'ouest-allemand' : "de",
    'ougandais' : "ug",
    'ouzbek' : "uz",
    'pakistanais' : "pk",
    'palestinien' : "ps",
    'panaméen' : "pa",
    'papouan-néo guinéen' : "pg",
    'paraguayen' : "py",
    'philippin' : "ph",
    'polonais' : "pl",
    'portoricain' : "pr",
    'portugais' : "pt",
    'péruvien' : "pe",
    'qatarien' : "qa",
    'Québecois' : "ca",
    'roumain' : "ro",
    'russe' : "ru",
    'rwandais' : "rw",
    'samoan' : "us",
    'saoudien' : "sa",
    'serbe' : "rs",
    'sierra-léonais' : "sl",
    'singapourien' : "sg",
    'slovaque' : "sk",
    'slovène' : "si",
    'somalien' : "so",
    'soudanais' : "sd",
    'soviétique' : "su",
    'sri-lankais' : "lk",
    'sud-africain' : "za",
    'sud-coréen' : "kr",
    'suisse' : "ch",
    'surinamien' : "sr",
    'suédois' : "se",
    'swazi' : "sz",
    'syrien' : "sy",
    'sénégalais' : "sn",
    'tadjik' : "tj",
    'tanzanien' : "tz",
    'taïwanais' : "tw",
    'tchadien' : "td",
    'tchèque' : "cz",
    'tchécoslovaque' : "cz",
    'thaïlandais' : "th",
    'togolais' : "tg",
    'tongien' : "to",
    'trinidadiens' : "tt",
    'tunisien' : "tn",
    'turc' : "tr",
    'turkmène' : "tm",
    'tuvaluan' : "",
    'U.S.A.' : "us",
    'ukrainien' : "ua",
    'uruguayen' : "uy",
    'vietnamien' : "vn",
    'vénézuélien' : "ve",
    'yougoslave' : "yu",
    'yéménite' : "ye",
    'zambien' : "zm",
    'zaïrois' : "",
    'zimbabwéen' : "",
    'égyptien' : "eg",
    'émirati' : "",
    'équato-guinéen' : "",
    'équatorien' : "ec",
    'éthiopien' : "et"
}
xx={'uk': (7313, 'britannique'), 'in': (1431, 'indien'), 'fr': (30204, 'français'), 'us': (37378, 'américain'), 'eg': (343, 'égyptien'), 'gr': (354, 'grec'), 'de': (6071, 'allemand'), 'se': (876, 'suédois'), 'sn': (95, 'sénégalais'), 'ca': (4339, 'canadien'), 'ch': (1257, 'suisse'), 'at': (731, 'autrichien'), 'cf': (77, 'centrafricain'), 'hk': (1061, 'hong-kongais'), 'it': (5518, 'italien'), 'kr': (901, 'sud-coréen'), 'af': (30, 'afghan'), 'cn': (1091, 'chinois'), 'br': (1058, 'brésilien'), 'pl': (652, 'polonais'), 'ar': (773, 'argentin'), 'ir': (479, 'iranien'), 'tr': (975, 'turc'), 'jp': (2806, 'japonais'), 'fi': (520, 'finlandais'), 'ru': (1198, 'russe'), 'rs': (112, 'serbe'), 'bg': (145, 'bulgare'), 'mk': (25, 'macédonien'), 'dz': (212, 'algérien'), 'be': (2324, 'belge'), 'ro': (290, 'roumain'), 'za': (245, 'sud-africain'), 'mx': (861, 'mexicain'), 'ua': (96, 'ukrainien'), 'dk': (725, 'danois'), 'ba': (55, 'bosniaque'), 'my': (43, 'malaisien'), 'cu': (174, 'cubain'), 'es': (2933, 'espagnol'), 'ie': (468, 'irlandais'), 'no': (397, 'norvégien'), 'hu': (500, 'hongrois'), 'cz': (561, 'tchécoslovaque'), 'sk': (155, 'slovaque'), 'pk': (33, 'pakistanais'), 'au': (1088, 'australien'), 'il': (674, 'israélien'), 'nz': (274, 'néo-zélandais'), 'sy': (58, 'syrien'), 'pt': (534, 'portugais'), 'uy': (69, 'uruguayen'), 'bf': (46, 'burkinabé'), 'is': (146, 'islandais'), 'tn': (181, 'tunisien'), 'pe': (127, 'péruvien'), 'lt': (97, 'lituanien'), 'ph': (213, 'philippin'), 'lu': (248, 'luxembourgeois'), 'tw': (253, 'taïwanais'), 'su': (183, 'soviétique'), 'cl': (248, 'chilien'), 'nl': (673, 'néerlandais'), 'ci': (32, 'ivoirien'), 'ge': (73, 'géorgien'), 'np': (14, 'népalais'), 'co': (185, 'colombien'), 'si': (62, 'slovène'), 'ye': (7, 'yéménite'), 'ng': (12, 'nigérien'), 'bj': (23, 'béninois'), '': (140, 'émirati'), 'ma': (259, 'marocain'), 'yu': (160, 'yougoslave'), 'li': (14, 'liechtensteinois'), 'qa': (92, 'qatarien'), 'ml': (36, 'malien'), 'cy': (22, 'chypriote'), 'hr': (112, 'croate'), 'lb': (237, 'libanais'), 'id': (74, 'indonésien'), 'sa': (8, 'saoudien'), 'sg': (69, 'singapourien'), 'th': (180, 'thaïlandais'), 'vn': (72, 'vietnamien'), 'mn': (19, 'mongol'), 'cg': (30, 'congolais'), 'ht': (51, 'haïtien'), 'bw': (4, 'botswanais'), 'kz': (62, 'kazakh'), 'gn': (19, 'guinéen'), 'mc': (8, 'Monegasque'), 'lk': (28, 'sri-lankais'), 'me': (8, 'monténégrin'), 'az': (13, 'azerbaïdjanais'), 'ee': (105, 'estonien'), 've': (94, 'vénézuélien'), 'ne': (55, 'nigérian'), 'lv': (97, 'letton'), 'dm': (24, 'dominicain'), 'ps': (100, 'palestinien'), 'mg': (12, 'malgache'), 'tj': (21, 'tadjik'), 'cm': (33, 'camerounais'), 'kh': (41, 'cambodgien'), 'sz': (4, 'swazi'), 'jm': (14, 'jamaïcain'), 'ni': (7, 'nicaraguéen'), 'gh': (10, 'ghanéen'), 'bh': (2, 'bahreini'), 'bo': (28, 'bolivien'), 'jo': (22, 'jordanien'), 'pr': (24, 'portoricain'), 'py': (12, 'paraguayen'), 'ag': (2, 'antiguais'), 'mr': (17, 'mauritanien'), 'rw': (8, 'rwandais'), 'ug': (7, 'ougandais'), 'kw': (12, 'kowetien'), 'al': (20, 'albanais'), 'ga': (9, 'gabonais'), 'td': (17, 'tchadien'), 'ke': (25, 'Kenyan'), 'zm': (6, 'zambien'), 'kg': (29, 'kirghiz'), 'am': (37, 'arménien'), 'ao': (8, 'angolais'), 'iq': (31, 'Irakien'), 'sd': (7, 'soudanais'), 'et': (13, 'éthiopien'), 'mu': (3, 'mauriciens'), 'gt': (19, 'guatémaltèque'), 'ec': (27, 'équatorien'), 'tg': (6, 'togolais'), 'pa': (12, 'panaméen'), 'sr': (1, 'surinamien'), 'la': (4, 'laotien'), 'bb': (2, 'barbadien'), 'tt': (3, 'trinidadiens'), 'bz': (4, 'belizien'), 'cr': (8, 'Costaricain'), 'uz': (7, 'ouzbek'), 'ly': (3, 'libyen'), 'kp': (14, 'nord-coréen'), 'md': (1, 'moldave'), 'na': (3, 'namibien'), 'hn': (3, 'hondurien'), 'mz': (9, 'mozambiquais'), 'tm': (1, 'turkmène'), 'pg': (5, 'papouan-néo guinéen'), 'so': (3, 'somalien'), 'mw': (3, 'malawites'), 'tz': (10, 'tanzanien'), 'bs': (2, 'bahaméen'), 'lr': (4, 'libérien'), 'bt': (5, 'bhoutanais'), 'mt': (6, 'maltais'), 'sl': (1, 'sierra-léonais'), 'ad': (1, 'andorran'), 'dj': (1, 'djiboutiens'), 'bi': (2, 'burundais'), 'to': (1, 'tongien'), 'bm': (1, 'Bermudien')}

class DbHeader:
    def __init__(self, root, userdata, line=None, array=None):
        self.userdata=userdata
        self.root=root
        if line:
            self.line=line
            if line[-1]=="\n": line=line[:-1]
            self.heads=line.split(";")
            while len(self.heads)>0 and self.heads[-1]=="":
                self.heads=self.heads[:-1]
        elif array:
            self.heads=array

        self.allheader=self.heads+self.userdata.heads()
        self.index={}
        for i in range(len(self.heads)):
            self.index[self.heads[i]]=i

    def __getitem__(self, item):
        if isinstance(item, int): return item
        else: return self.index[item]

    def allheads(self): return self.allheader


    def format(self, out=[]):
        if len(out):
            strout=""
            for x in out:
                if x in self.heads :
                    strout+=x+";"
                elif self.userdata and x in self.userdata.heads():
                    strout+=x+";"
                else:
                    raise Exception("Header '"+str(x)+"' does not exists")
            return strout
        else: return str(self)

    def __str__(self):
        out=""
        for x in self.heads+self.userdata.heads():
            out+=x+";"
        return out
    def __repr__(self): return self.__str__()

class DbRow:
    def __init__(self, head, userdata, line=None, array=None):
        self.id=None
        self.userdata=userdata
        self.header=head
        if line:
            self.line=line
            if line[-1]=="\n": line=line[:-1]
            lex=Lexer(StringIO(line))
            self.data=[]
            tok=Lexer.TOK_PVIRGULE
            while tok==Lexer.TOK_PVIRGULE:
                tok=lex.next()
                if tok in [Lexer.TOK_INT, Lexer.TOK_FLOAT, Lexer.TOK_STRING]:
                    self.data.append(lex.data)
                    tok=lex.next()
                elif tok==Lexer.TOK_PVIRGULE:
                    self.data.append(None)
                elif tok==Lexer.TOK_END:
                    break
                else:
                    raise Exception("Type "+Lexer.tokstr(tok)+" not expected (str, int, float)")
        elif array:
            x=len(self.header.heads)
            self.data=array[:x]
            if len(array)>x:
                self.userdata.put(self.data[0], array[x:])

        if len(self.header.heads)!=len(self.data):
            print(len(self.header.heads), self.header.heads)
            print(len(self.data), self.data)
            raise Exception("Bad number of columns")
        self.id=self.data[0]

    def __getitem__(self, item):
        return self.resolve(item)

    def function(self, name, args):
        return allofunction.call(self, name, args)

    def user(self, user):
        self.userdata=user

    def resolve(self, item):
        if item in self.header.heads: return self.data[self.header[item]]
        if self.userdata: return self.userdata.resolve(self.id, item)
        return None

    def format(self, out=[]):
        if len(out):
            strout=""
            for xx in out:
                x=self.resolve(xx)
                if isinstance(x, (float, int)): strout+=str(x)
                if isinstance(x, list):
                    strout+=json.dumps(x)
                elif isinstance(x, str): strout+='"'+x.replace('"', '\\"')+'"'
                strout+=";"
            return strout
        else: return str(self)

    @staticmethod
    def sortkey( a, b, key, coef):
        a=a[key]
        b=b[key]
        if a!=None and b!=None:
            if isinstance(a, str):
                a=a.lower()
                b=b.lower
            if a==b: return 0
            return -1*coef if ( a<b ) else 1*coef
        if a: return 1*coef
        elif b: return -1*coef
        return 0

    def _html_to_json(self, content):
        pass

    def add_from_json(self, js):
        arr=[]

    def add_from_html(self, url=None, file=None, content=""):
        if url:
            req=requests.get(url)
            if req.status_code!=200: return None
            content=req.text
        elif file:
            with open(file) as f:
                content=f.read()
        js=self._html_to_json(content)
        return self.add_from_json(js)

    def set(self, item, value=None):
        if isinstance(item, list):
            for x in item:
                k, v = x
                self.set(k,v)
            return

        if item in self.header.heads:
            for i in range(len(self.header.heads)):
                if item==self.header.heads[i]:
                    self.data[i]=value
                    return

        self.userdata.set(self.id, item, value)

    def json(self, format=[]):
        if len(format)==0: format=self.header.allheads()
        out={}
        for x in format:
            out[x]=self.resolve(x)
        return out

    def __str__(self):
        out=""
        for x in self.data+self.userdata.array(self.id):
            if isinstance(x, (float, int)): out+=str(x)
            if isinstance(x, list): out+=json.dumps(x)
            elif isinstance(x, str): out+='"'+x.replace('"', '\\"')+'"'
            out+=";"
        return out
    def __repr__(self): return self.__str__()

class DB:
    COLUMNS=[
                           ("id", None, None, "id"),
                           ("name", None, None, "name"),
                           ("image/url", None, None, "image"),
                           ("pays/*", utils.castarr, None, "nationality"),
                           ("annee",  None, None, "year"),
                           ("genre/*", utils.castarr, None, "genre"),
                           ("description",  None, None, "description"),
                           ("director/*/name", None, None, "director"),
                           ("actor/*/name", utils.castarr, None, "actor"),
                           ("creator/*/name", utils.castarr, None, "creator"),
                           ("musicBy/*/name", utils.castarr, None, "musicBy"),
                           ("aggregateRating/ratingValue", utils.floatvirg, None, "note"),
                           ("aggregateRating/ratingCount", int, None, "nnote"),
                           ("aggregateRating/reviewCount", int, None, "nreview")
                       ]

    @staticmethod
    def COLUMNS_NAME():
        out=[]
        for x in DB.COLUMNS: out.append(x[3])
        return out

    def __init__(self, root, file=None, userdata=None, col=[], order=[]):
        self.root=root
        self.file=file
        self.header=None
        self.needsave=False
        self.userdata=userdata
        self.data=[]
        self.columns=col
        self.order=order
        self.time=time.time()
        if file:
            with open(file, "r") as f:
                self.header=DbHeader(self, userdata, line=f.readline())
                line=f.readline()
                while line!="":
                    self.data.append(DbRow(self.header,line=line))
                    line=f.readline()
                self.time = time.time() - self.time
                #print("line -> ", line)
        else:
            self.header=DbHeader(self, userdata, array=DB.COLUMNS_NAME())

    def function(self, name, args):
        return allofunction.call(self, name, args)

    def moustache(self):
        arr=[]
        for x in self.data:
            arr.append(x.json(self.columns))
        return {
            "count" : len(self.data),
            "time" : int(self.time*1000)/1000,
            "data" : arr
        }

    def list_pays(self):
        out=[]
        for x in  self.data:
            payss=x.resolve("nationality")
            if payss:
                tmp=[]
                for pays in payss:
                    tmp.append(payslist[pays])
                x.data[3]=tmp
        return out

    def __str__(self):
        out=str(self.length())+" résultats en "+str( int(self.time*1000000)/1000)+" ms\n"
        out+=str(self.header.format(self.columns))+"\n"
        for x in self.data:
            out+=x.format(self.columns)+"\n"
        return out

    def __repr__(self): return self.__str__()

    def length(self): return len(self.data)

    def _root(self): return self.root._root() if self.root else self

    def put(self, expr):
        array=expr.val(self)
        self.data.append(DbRow(self.header, self.userdata, array=array))
        if self.root==None: self.needsave=True
        return True

    def commit(self):
        if self.root: return self.root.commit()
        else:
            if self.needsave:
                self.save(self.file)
            if self.userdata.changed():
                self.userdata.save()
            self.needsave=False

    def set(self, affs, expr):
        rows=self.match(expr)
        for x in rows.data:
            x.set(affs)

    def execute(self, expr):
        if isinstance(expr, str): expr=Parser.parsestring(expr, self.userdata)
        if isinstance(expr, alloexpr.BlocExpr):
            ret=None
            for x in expr.insts:
                ret=self.execute(x)
            return ret

        if isinstance(expr, alloexpr.SetExpr):
            aff=expr.afflist
            ex=expr.expr
            return self.set(aff, ex)
        elif isinstance(expr, alloexpr.ArrayExpr): return self.put(expr)
        elif isinstance(expr, alloexpr.SelectExpr): return self.match(expr)
        return expr.val(self)

    def emptyset(self):
        out = None
        out = DB(self._root(), userdata=self.userdata)
        out.header = self.header
        return out

    def row_at(self, n):
        return self.data[n]

    def match(self, expr):
        out=None
        if isinstance(expr, alloexpr.SelectExpr):
            out=DB(self._root(), userdata=self.userdata, col=expr.select, order=expr.order)
        else:
            out=DB(self._root(), userdata=self.userdata)
        out.header=self.header
        i=0
        for row in self.data:
            try:
                if expr.val(row):
                    out.data.append(row)
            except TypeError:
                pass
            i+=1
        if len(out.order)>0:
            key, sens = out.order[0]
            out.data=sorted(out.data, key=cmp_to_key(lambda a,b: DbRow.sortkey(a,b, key, 1 if sens else -1) ))
        out.time = time.time() - out.time

        return out

    def __len__(self):
        return len(self.data)

    def list_personnes(self, field="actor"):
        out = {}
        arr = []
        for row in self.data:
            names = row.resolve(field)
            if names:
                for name in names:
                    name = name.lower()
                    if not name in out:
                        out[name] = (1, [row.resolve("id")])
                    else:
                        out[name] += (out[name][0] + 1, out[name][1] + [row.resolve("id")])
        for x in out:
            arr.append((x, out[x]))
        arr = sorted(arr, key=lambda x: x[1][0], reverse=True)
        return arr

    def list_array_field_value(self, field):
        out={}
        for row in self.data:
            names=row.resolve(field)
            if names:
                for name in names:
                    name=name.lower()
                    if not name in out:
                        out[name]=True
        return out.keys()


    @staticmethod
    def fromjson(js, userdata):
        if isinstance(js, str):
            with open(js, "r") as f:
                js=json.loads(f.read())
        db=DB(None, userdata=userdata)
        db.time=js["time"]
        db.header=DbHeader(db, userdata, array=js["columns"])
        db.order=js["order"]
        for row in js["data"]:
            db.data.append(DbRow(db.header, userdata=userdata,  array=row))

        return db

    def addfromhtml(self, content):
        self.data.append(DbRow(self.header, userdata=self.userdata, array=utils.extract(content, DB.COLUMNS)))

    def tojson(self):
        rows=[]
        for x in self.data:
            rows.append(x.data)
        return {
            "time": self.time,
            "columns" : self.header.heads,
            "results": len(self.data),
            "order" : self.order,
            "data" :  rows
        }

    def save(self, file):
        with open(file, "w") as f:
            f.write(json.dumps(self.tojson()))


    def bons_film(self, n=1, annees=None, genres=None):
        base='select * where (note in range(3.5,5)) '
        if annees:
            base+=" and ("
            if isinstance(annees, int): base+="year="+str(annees)
            else: base+="year in range("+str(annees[0])+","+str(annees[1])+")"
            base+=")"
        if annees:
            base+=" and ("
            if isinstance(annees, str): base+=' ("'+genres+'" in genre)'
            else:
                for i in range(len(genres)):
                    genre=genres[i]
                    base += (" or " if i>0 else "")+' ("' + genre + '" in genre)'
            base+=")"
        base+=" order by note desc"
        print(base)
        return self.execute(base)

def printreq(adb, req):
    res=adb.execute(req)
    print(res)

def ____():
    t=time.time()
    #adb = AlloDB("result.csv")

    usr = user.User.createuser("Test")
    adb = DB.fromjson("db.json", usr)
    t=time.time()-t
    print(t, "s \n")

    #printreq(adb, 'set ownnote=2.5 where id=224')
    """
    select='put [1000224,' \
    '"Les Larmes amères de Petra von Kant",' \
    '"http://fr.web.img5.acsta.net/pictures/18/04/13/17/04/2768861.jpg",' \
    '["de"],1972,["Drame"],' \
    '"Une femme de la grande bourgeoisie, creatrice de mode, vit une passion douloureuse avec une jeune femme de condition plus modeste, Karin, qui reve de devenir mannequin.",' \
    '["Rainer Werner Fassbinder"],' \
    '["Margit Carstensen", "Hanna Schygulla", "Irm Hermann", "Eva Mattes"],' \
    '["Rainer Werner Fassbinder"],["Giuseppe Verdi"],3.8,97,19, 0,1,2,3];id=1000224'
    """

    #printreq(adb, 'count(select id where id in range(1,100))')
    #printreq(adb, 'rand(select id where "ken loach" in director, 5)')
    print(adb.bons_film(10, (2010,2020), ("policier", "thriller")))
    #print(adb.list_array_field_value("genre", ))
    while True:
        sys.stdout.write("$ ")
        sys.stdout.flush()
        x=sys.stdin.readline()
        try:
            res=adb.execute(x)
            print(res)
        except:
            traceback.print_exc()
