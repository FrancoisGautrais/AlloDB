
# block		::=  inst [ ';' inst ]* ';'
# inst		::= select | set | put
# put		::= 'put'  expr [',' expr]*
# set		::= 'set'  IDENT '=' expr [',' IDENT '=' expr]*  where expr
# aff		::= IDENT '=' expr
# selct		::= ['select' [ [IDENT [',' IDENT]* ] ] 'where'] expr [order by IDENT [desc]]
# expr	 	::= exprOr
# exprOr  	::= exprAnd | exprAnd ('or' | 'and') exprOr
# exprAnd  	::= exprIn | exprIn ('&&' | 'or') exprAnd
# exprIn  	::= exprBOr | exprBOr 'in' exprIn
# exprBOr 	::= exprBAnd | exprBAnd '|' exprBOr
# exprBAnd 	::= exprNot | exprNot '&' exprBAnd
# exprNot 	::= exprComp | 'not' exprNot
# exprComp	::= exprAdd | exprAdd ( '=' | '!=' | '<' | '<=' | '>' | '>=' ) exprComp
# exprAdd 	::= exprMul | exprMul ( '+' | '-' ) exprAdd
# exprMul 	::= prim | prim ( '*' | '/' | '%' ) exprMul
# prim 		::= '(' expr ')' | NUMBER | array | IDENT
# array 	::= '[' [expr] [ ',' expr ]* ] ']'

class Context(dict):
    def __init__(self, d=None):
        if not d: d={}
        dict.__init__(self, d)

    def resolve(self, key : str ):
        return self.__getitem__(key)

class Expr:
    def __init__(self):
        pass

    def type(self):
        return self.__class__

    def __str__(self):
        raise Exception("Not implemented")

    def __repr__(self): return self.__str__()
    def val(self, dico): raise Exception("Not implemented")

    def isconst(self): return self.first.isconst()
    def optimize(self): return ConstExpr(self.val(None)) if self.isconst() else self




class UnaryExpr(Expr):
    def __init__(self, data, optim=True):
        Expr.__init__(self)
        self.first=data.optimize() if isinstance(data, Expr) and optim else data

    def isconst(self): return self.first.isconst()

class BinaryExpr(Expr):
    def __init__(self, first, second, sign):
        Expr.__init__(self)
        self.first=first.optimize() if isinstance(first, Expr) else first
        self.second=second.optimize() if isinstance(second, Expr) else second
        self.sign=sign

    def __str__(self): return "("+str(self.first)+" "+self.sign+" "+str(self.second)+")"

    def isconst(self):
        return self.first.isconst() and self.second.isconst()

class ConstExpr(UnaryExpr):
    def __init__(self, data):
        UnaryExpr.__init__(self, data, False)

    def __str__(self): return str(self.first)

    def isconst(self): return True

    def optimize(self): return self
    def val(self, dico):
        return self.first

class ArrayExpr(ConstExpr):
    def val(self, dico):
        out=[]
        for i in range(len(self.first)):
            out.append(self.first[i].val(dico))
        return out

class TupleExpr(ConstExpr):
    def val(self, dico):
        out=[]
        for i in range(len(self.first)):
            out.append(self.first[i].val(dico))
        return out

class VarExpr(UnaryExpr):
    def __init__(self, data, user):
        if not isinstance(data, str): raise Exception("Var must be ident")
        UnaryExpr.__init__(self, data)
        self.userdata=user

    def __str__(self): return self.first

    def isconst(self): return False
    def val(self, dico):
        return dico.resolve(self.first)

class EqExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "=")
    def val(self, dico):
        f=self.first.val(dico)
        s=self.second.val(dico)
        return (f.lower()==s.lower()) if isinstance(f, str) else f==s

class LtExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "<")
    def val(self, dico): return self.first.val(dico) < self.second.val(dico)

class GtExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, ">")
    def val(self, dico): return self.first.val(dico) > self.second.val(dico)

class LeExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "<=")
    def val(self, dico): return self.first.val(dico)<=self.second.val(dico)

class GeExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, ">=")
    def val(self, dico): return self.first.val(dico)>=self.second.val(dico)

class NeExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "!=")
    def val(self, dico): return self.first.val(dico)!=self.second.val(dico)

class AddExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "+")
    def val(self, dico): return self.first.val(dico) + self.second.val(dico)

class SubExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "-")
    def val(self, dico): return self.first.val(dico) - self.second.val(dico)

class MultExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "*")
    def val(self, dico): return self.first.val(dico) * self.second.val(dico)

class DivExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(f, s, "/")
    def val(self, dico): return self.first.val(dico) / self.second.val(dico)

class ModExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self,f, s, "%")
    def val(self, dico): return self.first.val(dico) % self.second.val(dico)

class OrExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self,f, s, "and")
    def val(self, dico): return self.first.val(dico) or self.second.val(dico)

class AndExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "or")
    def val(self, dico): return self.first.val(dico) and self.second.val(dico)

class BorExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self,f, s, "&")
    def val(self, dico): return self.first.val(dico) or self.second.val(dico)

class  BandExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "|")
    def val(self, dico): return self.first.val(dico) and self.second.val(dico)


class InExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, "in")
    def val(self, dico):
        f=self.first.val(dico)
        s=self.second.val(dico)
        if f==None or s==None: raise TypeError("")
        if isinstance(s, str): return f.lower() in s.lower()
        if isinstance(s, list):
            if f in s:
                return s
            if isinstance(f, str):
                f=f.lower()
                for x in s:
                    if isinstance(x, str) and f in x.lower():
                        return True
                return False
        if isinstance(s, (Range)): return s.is_in(f)
        raise Exception("Type error in IN")

class Range:
    def __init__(self, start, end):
        self.start=start
        self.end=end

    def is_in(self, x):
        return x>=self.start and x<=self.end

    def is_out(self, x):
        return not self.is_in(x)

class  RangeExpr(BinaryExpr):
    def __init__(self, f, s): BinaryExpr.__init__(self, f, s, None)
    def val(self, dico):
        return Range(self.first.val(dico), self.second.val(dico))
    def __str__(self): return "range("+str(self.first)+", "+str(self.second)+")"


class NotExpr(UnaryExpr):
    def __init__(self, f): UnaryExpr.__init__(self,f)
    def val(self, dico): return not self.first.val(dico)
    def __str__(self): return "not ("+str(self.first)+")"

class BlocExpr(Expr):
    def __init__(self, bloc):
        Expr.__init__(self)
        self.insts=bloc

    def val(self, dico):
        return None

    def __str__(self):
        out=""
        for x in self.insts:
            out+=str(x)+";"
        return out

    def isconst(self):
        for x in self.afflist:
            if not x[1].isconst():
                return False
        return self.expr.isconst()

    def optimize(self): return self

class SetExpr(Expr):
    def __init__(self, afflist, expr):
        Expr.__init__(self)
        self.afflist=afflist
        self.expr=expr

    def val(self, dico):
        return dico.set(self.afflist, self.expr)

    def __str__(self): return "( set "+str(self.afflist)+" where "+str(self.expr)+")"

    def isconst(self):
        for x in self.afflist:
            if not x[1].isconst():
                return False
        return self.expr.isconst()

    def optimize(self): return self

class FunctionCall(Expr):
    def __init__(self, name, params):
        Expr.__init__(self)
        self.name=name
        self.params=params

    def __str__(self):
        out=self.name+"("
        for i in range(len(self.params)):
            out+=("; " if i>0 else "")+self.params[i]
        return out+")"


    def isconst(self): return False

    def val(self, dico):
        return dico.function(self.name, self.params)


class SelectExpr(Expr):
    def __init__(self, select, expr, order):
        Expr.__init__(self)
        self.select=select
        self.first=expr
        self.order=order

    def __str__(self):
        out=""
        if self.select:
            out+="select"
            for i in range(len(self.select)):
                out+=(", " if (i>0) else " ")+self.select[i]
            out+=" where "
        out+=str(self.first)
        if self.order:
            out+=" order by "
            for i in range(len(self.order)):
                ident, sens = self.order[i]
                out+=("," if i>0 else "")+ident+" "+("asc" if sens else "desc")
        return out

    def val(self, dico):
        return self.first.val(dico)


    def optimize(self):
        self.first = ConstExpr(self.val(None)) if self.isconst() else self.first
        return self
