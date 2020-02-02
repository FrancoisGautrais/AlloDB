import json

import requests
from io import StringIO

import allofunction
from allolexer import Lexer


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

        self.allheader=self.heads+(self.userdata.heads() if self.userdata else [])
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

        self.userdata.set(str(self.id), item, value)

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
