from allolexer import Lexer
from io import StringIO

class Context(dict):
    def __init__(self, d=None):
        if not d: d={}
        dict.__init__(self, d)

    def resolve(self, key : str ):
        return self.__getitem__(key)

class Expr:
    def __init__(self):
        pass

    def __str__(self):
        raise Exception("Not implemented")

    def __repr__(self): return self.__str__()
    def val(self, dico): raise Exception("Not implemented")

    def isconst(self): return self.first.isconst()
    def optimize(self): return ConstExpr(self.val(None)) if self.isconst() else self


    @staticmethod
    def parsestring(string, data):
        io = StringIO(string)
        l=Lexer(io)
        parser=Parser(l, data)
        return parser.parse().optimize()


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
            if f in s: return s
            if isinstance(f, str):
                f=f.lower()
                for x in s:
                    if isinstance(x, str) and x.lower() in s: return True
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
    def val(self, dico): return not self.second.val(dico)
    def __str__(self): return "not ("+str(self.first)+")"


class RootExpr(Expr):

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

class Parser:
    def __init__(self, lexer, data):
        self.lex=lexer
        self.data=data
        self.tok = Lexer.TOK_UNKNOWN

    def _main(self):
        ret = None
        ret = self._instList()
        return ret

    def _next(self):
        self.tok = self.lex.next()
        self.data = self.lex.data
        # print("Token", Lexer.tokstr(self.tok), " '" + str(self.data) + "'")
        return self.tok

    def parse(self):
        self._next()
        return self._root()


    def _root(self):
        select=[]
        expr=None
        order=[]
        if self.tok==Lexer.TOK_IDENT and self.lex.current=="select":
            self._next()

            while True:
                if self.tok!=Lexer.TOK_IDENT and self.tok!=Lexer.TOK_STRING:
                    raise Exception("Ident expected in select statement")
                select.append(self.lex.data)
                self._next()
                if self.tok==Lexer.TOK_VIRGULE:
                    self._next()
                elif self.lex.data=="where":
                    self._next()
                    break
                else:
                    raise Exception("Where expected after select statement")

        expr=self._expr()

        if self.tok==Lexer.TOK_IDENT and self.lex.current=="order":
            self._next()
            if self.tok==Lexer.TOK_IDENT and self.lex.current=="by": self._next()
            while self.tok == Lexer.TOK_IDENT or self.tok==Lexer.TOK_STRING:
                x=self.lex.data
                self._next()
                if self.tok == Lexer.TOK_IDENT:
                    if self.lex.data=="desc": order.append((x, False))
                    else: order.append((x,True))
                else: order.append((x, True))
                self._next()

        return RootExpr(select, expr, order)

    def _expr(self): return self._exprOr()

    def _exprOr(self):
        first = self._exprAnd()
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_OR: return first

        self._next()
        second = self._exprOr()
        return OrExpr(first, second)

    def _exprAnd(self):
        first = self._exprIn()  #####
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_AND: return first

        self._next()
        second = self._exprAnd()
        return AndExpr(first, second)

    def _exprIn(self):
        first = self._exprBOr() #####
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_IN: return first

        self._next()
        second = self._exprIn()
        return InExpr(first, second)

    def _exprBOr(self):
        first = self._exprBAnd()
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_BOR: return first

        self._next()
        second = self._exprAnd()
        return BorExpr(first, second)

    def _exprBAnd(self):
        first = self._exprNot()
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_BAND: return first

        self._next()
        second = self._exprAnd()
        return BandExpr(first, second)

    def _exprNot(self):
        if self.tok == Lexer.TOK_NOT:
            self._next()
            x = self._exprNot()
            return NotExpr(x)
        else:
            return self._exprComp()

    def _exprComp(self):
        first = self._exprAdd()
        op = self.tok
        opstr = self.data
        if op != Lexer.TOK_CMP: return first

        self._next()
        second = self._exprComp()
        if opstr=="=": return EqExpr(first, second)
        if opstr=="!=": return NeExpr(first, second)
        if opstr=="<": return LtExpr(first, second)
        if opstr=="<=": return LeExpr(first, second)
        if opstr==">": return GtExpr(first, second)
        if opstr==">=": return GeExpr(first, second)
        raise Exception("Error !")

    def _exprAdd(self):
        first = self._exprMul()
        op = self.tok
        if not (op in [Lexer.TOK_ADD, Lexer.TOK_SUB]): return first

        self._next()
        second = self._exprAdd()
        if op == Lexer.TOK_ADD: return AddExpr(first, second)
        return SubExpr(first, second)

    def _exprMul(self):
        first = self._prim()
        op = self.tok

        if not (op in [Lexer.TOK_MUL, Lexer.TOK_DIV, Lexer.TOK_MODULO]):    return first

        self._next()
        second = self._exprMul()
        if op == Lexer.TOK_MODULO: return ModExpr(first, second)
        if op == Lexer.TOK_MUL: return MultExpr(first, second)
        if op == Lexer.TOK_DIV: return DivExpr(first, second)

    PRIM_PREMIER = [Lexer.TOK_PO, Lexer.TOK_INT, Lexer.TOK_FLOAT, Lexer.TOK_IDENT, Lexer.TOK_BOOL, Lexer.TOK_STRING,
                    Lexer.TOK_CO]

    def _prim(self):
        if not (self.tok in Parser.PRIM_PREMIER): raise Exception(
            "_exprMul: Attendu '(', int ou float : " + Lexer.tokstr(self.tok))

        # (
        if self.tok == Lexer.TOK_PO:
            self._next()
            x = self._expr()
            if self.tok != Lexer.TOK_PF:
                raise Exception("Parenthese fermante manquante=> " + Lexer.tokstr(self.tok))
            self._next()
            return x
        # Number
        if self.tok in [Lexer.TOK_INT, Lexer.TOK_FLOAT, Lexer.TOK_BOOL, Lexer.TOK_STRING]:
            ret = ConstExpr(self.data)
            self._next()
            return ret
        if self.tok == Lexer.TOK_CO:
            return self._array()
        # ident
        if self.tok == Lexer.TOK_IDENT:
            x=self.lex.current
            self._next()
            if x=="range":
                if self.tok==Lexer.TOK_PO:
                    self._next()
                    first=self._exprAdd()
                    if self.tok==Lexer.TOK_VIRGULE:
                        self._next()
                        second=self._exprAdd()
                        if self.tok==Lexer.TOK_PF:
                            self._next()
                            return RangeExpr(first, second)

                raise Exception("Range need 2 parameters")
            return VarExpr(x, self.data)
        raise Exception("Attendu: int, float ou '(' => " + Lexer.tokstr(self.tok))

    def _array(self):
        if self.tok != Lexer.TOK_CO: raise Exception("'[' expected")
        self._next()
        x = []

        if self.tok == Lexer.TOK_CF:
            self._next()
            return ArrayExpr(x)

        x.append(self._expr())

        while self.tok == Lexer.TOK_VIRGULE:
            self._next()
            x.append(self._expr())

        if self.tok != Lexer.TOK_CF: raise Exception("Array must end with ']'")
        self._next()
        return ArrayExpr(x)

