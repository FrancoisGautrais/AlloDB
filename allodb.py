import sys
import time
import traceback
from functools import cmp_to_key
from alloexpr import Expr
from allolexer import Lexer
from io import StringIO

class AlloDbHeader:

    def __init__(self, line):
        self.line=line
        if line[-1]=="\n": line=line[:-1]
        self.heads=line.split(";")
        while len(self.heads)>0 and self.heads[-1]=="":
            self.heads=self.heads[:-1]
        self.index={}
        for i in range(len(self.heads)):
            self.index[self.heads[i]]=i

    def __getitem__(self, item):
        if isinstance(item, int): return item
        else: return self.index[item]


    def format(self, out=[]):
        if len(out):
            strout=""
            for x in out:
                if not x in self.heads:
                    raise Exception("Header '"+str(x)+"' does not exists")
                strout+=x+";"
            return strout
        else: return str(self)

    def __str__(self):
        out=""
        for x in self.heads:
            out+=x+";"
        return out
    def __repr__(self): return self.__str__()

class AlloDbRow:
    def __init__(self, head, line):
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


        self.header=head
        if len(self.header.heads)!=len(self.data):
            print(len(self.header.heads), self.header.heads)
            print(len(self.data), self.data)
            raise Exception("Bad number of columns")

    def __getitem__(self, item):
        return self.resolve(item)

    def resolve(self, item):
        return self.data[self.header[item]]


    def format(self, out=[]):
        if len(out):
            strout=""
            for xx in out:
                x=self.resolve(xx)
                if isinstance(x, (float, int)): strout+=str(x)
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

    def __str__(self):
        out=""
        for x in self.data:
            if isinstance(x, (float, int)): out+=str(x)
            elif isinstance(x, str): out+='"'+x.replace('"', '\\"')+'"'
            out+=";"
        return out
    def __repr__(self): return self.__str__()

class AlloDB:

    def __init__(self, file=None, col=[], order=[]):
        self.header=None
        self.data=[]
        self.columns=col
        self.order=order
        self.time=time.time()
        if file:
            with open(file, "r") as f:
                self.header=AlloDbHeader(f.readline())
                line=f.readline()
                while line!="":
                    self.data.append(AlloDbRow(self.header,line))
                    line=f.readline()
                self.time = time.time() - self.time
                #print("line -> ", line)

    def __str__(self):
        out=str(self.length())+" résultats en "+str( int(self.time*1000000)/1000)+" ms\n"
        out+=str(self.header.format(self.columns))+"\n"
        for x in self.data:
            out+=x.format(self.columns)+"\n"
        return out

    def __repr__(self): return self.__str__()

    def length(self): return len(self.data)

    def match(self, expr):
        if isinstance(expr, str): expr=Expr.parsestring(expr)
        out=AlloDB(col=expr.select, order=expr.order)
        out.header=self.header
        for row in self.data:
            try:
                if expr.val(row):
                    out.data.append(row)
            except TypeError:
                pass
        if len(expr.order)>0:
            key, sens = expr.order[0]
            out.data=sorted(out.data, key=cmp_to_key(lambda a,b: AlloDbRow.sortkey(a,b, key, 1 if sens else -1) ))
        out.time = time.time() - out.time

        return out


select=Expr.parsestring('select id, name, note where "will smith" in actor order by note desc')
t=time.time()
adb = AlloDB("result.csv")
t=time.time()-t
print(t, "s \n")
#select='note>=4 and nnote in range(100, 2000) and "Thriller" in genre'

res=adb.match(select)
print(res)

while True:
    sys.stdout.write("$ ")
    sys.stdout.flush()
    x=sys.stdin.readline()
    try:
        res=adb.match(x)
        print(res)
    except:
        traceback.print_exc()
