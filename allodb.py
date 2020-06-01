from resultset import ResultSet
import json
from allolist import AlloListSet
from sqlite_connector import SQConnector, sqvalue
import os
import sys
import utils
import time
import traceback
from allodbrow import DbRow, DbHeader
from functools import cmp_to_key

import allofunction
import user
import alloexpr
import requests

import alloimport
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


class DB(SQConnector):
    COLUMNS=[
                           ("id", None, -1, "id"),
                           ("name", None, "", "name"),
                           ("image/url", None, "", "image"),
                           ("pays/*", alloimport.castpays, [], "nationality"),
                           ("annee",  None, 0, "year"),
                           ("duration",  alloimport.castduration, 0, "duration"),
                           ("genre/*", alloimport.castarr, [], "genre"),
                           ("description",  None, "", "description"),
                           ("director/*/name", None, [], "director"),
                           ("actor/*/name", alloimport.castarr, [], "actor"),
                           ("creator/*/name", alloimport.castarr, [], "creator"),
                           ("musicBy/*/name", alloimport.castarr, [], "musicBy"),
                           ("aggregateRating/ratingValue", alloimport.floatvirg, 0, "note"),
                           ("aggregateRating/ratingCount", int, 0, "nnote"),
                           ("aggregateRating/reviewCount", int, 0, "nreview")
                       ]

    @staticmethod
    def COLUMNS_NAME():
        out=[]
        for x in DB.COLUMNS: out.append(x[3])
        return out

    def __init__(self, file):
        SQConnector.__init__(self, file)
        self.time=time.time()
        self.init_user("fanch", "user/fanch.json")

    def function(self, name, args):
        return allofunction.call(self, name, args)

    def row_from_id(self, user, id):
        return self.find(user, "id=%d" % id)

    def row_from_actor(self, user, act):
        return self.find(user, "'%s' in actor" % act)

    def row_from_director(self, dir):
        return self.find(user, "'%s' in director" % dir)

    def row_from_nationality(self, pays):
        return self.find(user, "'%s' in nationality" % pays)



    def __str__(self):
        return str(self.length())+" résultats en "+str( int(self.time*1000000)/1000)+" ms\n"


    def __repr__(self): return self.__str__()


    def length(self): return len(self.one("select count(*) from films"))

    def list_get(self, user):
        ret = self.exec("select filmid, lists from %s where lists!=''" % user)
        out={}
        for row in ret:
            id=row[0]
            lists=row[1].split(",")
            for ids in lists:
                if not ids in out:
                    out[ids]={
                        "name" : self.one("select name from %s_lists where id='%s'" % (
                            user, ids
                        )),
                        "list" : [],
                        "id" : ids
                    }
                out[ids]["list"].append(id)
        return out

    def list_get_films(self, user, id):
        cur=self.conn.cursor()
        cur.execute("select * from films,%s where filmid=id and lists like '%%%s%%'" % (
            user, id
        ))
        als=AlloListSet()
        als.set_list(cur, id, self.one("select name from %s_lists where id='%s' "%(
            user, id
        )))
        return als

    def get_list_by_id(self, user, id):
        return self.resultset("select filmid, lists from %s where lists like '%%%s%%'" % (user, id), pagesize=-1)

    def list_remove(self, user, id):
        for row in self.exec("select id, lists from %s where lists like '%%%s%%' " % (user, id)):
            fid = row[0]
            l = row[1].split(",")
            ll = []
            for x in l:
                if l != id: ll.append()
            self.exec("update %s set lists='%s' where id=%d " % (user, ",".join(ll), fid))
        self.exec("delete from %s_lists where id=%d" % (user, id))

    def list_remove_item(self, user, lid, fid):
        l=self.one("select lists from %s where id=%d " % (user, fid))
        ll=[]
        for tmp in l.split(","):
            if tmp!=lid: ll.append(tmp)
        self.exec("update %s set lists='%s' where id=%d "%(user, ",".join(ll), fid))

    def list_add_item(self, user, fid, lid):
        l=self.one("select lists from %s where id=%d " % (user, fid))
        if len(l): l+=","
        l+=lid
        self.exec("update %s set lists='%s' where id=%d" % (user, l, fid))

    def list_create(self, user, name):
        self.exec("insert into %s_lists (id, name) values ('%s', '%s') "%(
            user, utils.new_id(), name
        ))

    def list_rename(self, user, lid, name):
        self.exec("update %s_lists set name='%s' where id=%d" % (user, name, lid))

    def request_add(self, user, name, value):
        self.exec("insert into %s_requests set (name, value) values ('%s', '%s')" % (user, name,
                 json.dumps(value)))

    def request_update(self, user, name, value):
        self.exec("update %s_requests set value='%s' where name='%s' " % (
            user, json.dumps(value), name
        ))

    def request_get(self, user):
        out={}
        for row in self.exec("select name,value from %s_requests" % user):
            out[row[0]]=json.loads(row[1])
        return out

    def request_remove(self, user, name):
        self.exec("delete from %s_requests where name='%s'" % (user, name))


    def append(self, row):
        if isinstance(row, (list, tuple)): row=DbRow(self.header, None, array=row)
        self.data.append(row)
        id=row.resolve("id")
        self.ids[id]=row
        actors=row.resolve("actor")
        if actors:
            for actor in actors:
                actor=actor.lower()
                if not actor in self.actors: self.actors[actor]=[]
                self.actors[actor].append(row)
        directors=row.resolve("director")
        if directors:
            for director in directors:
                director=director.lower()
                if not director in self.directors: self.directors[director]=[]
                self.directors[director].append(row)
        pays=row.resolve("nationality")
        if pays:
            for pay in pays:
                pay=pay.lower()
                if not pay in self.pays: self.pays[pay]=[]
                self.pays[pay].append(row)
        iid=int(id)
        if iid>self.last_id: self.last_id=iid

    def put(self, expr):
        array=expr.val(self)
        self.data.append(DbRow(self.header, self.userdata, array=array))
        self.needsave=True
        return True


    def set(self, user, affs, id):
        out="update %s set " % user
        i=0
        for x in affs:
            if i>0: out+=", "
            out+=x+"="
            out+=sqvalue(affs[x])
            i+=1
        self.conn.execute(out + " where id=%d" % id)


    def autocomplete(self, pattern, type, max=-1):
        query= "select name, year from films where %s like '%%%s%%' " % (type, pattern)
        out={}
        if max:
            query+=" LIMIT %d" % max

        for row in self.exec(query):
            out[row[0]+" ("+str(row[1])+")"]=id
        return out

    def __len__(self):
        return len(self.data)



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
            db.append(DbRow(db.header, userdata=userdata,  array=row))

        return db

    def addfromhtml(self, content):
        self.data.append(DbRow(self.header, userdata=self.userdata, array=alloimport.extract(content, DB.COLUMNS)))

    def tojson(self):
        rows=[]
        for x in self.data:
            rows.append(x.data)
        return {
            "time": self.time,
            "columns" : self.header.heads,
            "results": len(self.data),
            "order" : self.order,
            "data" :  rows,
            "last_id" : self.last_id
        }



    def extract_html_dir(self, dir):
        n=0
        MAX=1382
        for x in os.listdir(dir):
            if n%MAX==0: print(int(n/MAX), " % : ", len(self.data))
            p=os.path.join(dir, x)
            with open(p, "r") as f:
                self.append(alloimport.extract(f.read(), DB.COLUMNS))
            n+=1

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

def createdb():
    db=DB(None)
    db.extract_html_dir("/home/fanch/allocine/allocine/")
    db.save("db.json")

if __name__=="__main__":
    createdb()
