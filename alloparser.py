from allolexer import Lexer
from io import StringIO

from alloexpr import *

class Parser:


    @staticmethod
    def parsestring(string, data):
        io = StringIO(string)
        l=Lexer(io)
        parser=Parser(l, data)
        return parser.parse().optimize()

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
        return self._block()

    def _block(self):
        out=[]
        while True:
            x=self._inst()
            out.append(x)
            if self.tok==Lexer.TOK_END:
                return BlocExpr(out)
            if not self.tok==Lexer.TOK_PVIRGULE:
                raise Exception("';' expected after instruction")
            self._next()

    def _inst(self):
        if self.tok==Lexer.TOK_IDENT:
            if self.data=="set": return self._set()
            if self.data=="put": return self._put()
            if self.data=="select": return self._select()
        return self._expr()

    def _put(self):
        if self.tok==Lexer.TOK_IDENT and self.lex.data=="put":
            self._next()
            return self._array()

    def _set(self):
        affs=[]
        expr=None
        if self.tok==Lexer.TOK_IDENT and self.lex.data == "set":
            self._next()
            affs.append(self._aff())
            while self.tok==Lexer.TOK_VIRGULE:
                affs.append(self._aff())

            if self.tok!=Lexer.TOK_IDENT or self.data!="where":
                raise Exception("'where' expected affectatiopn in set")
            self._next()
            expr=self._expr()
        return SetExpr(affs, expr)

    def _aff(self):
        a=""
        out=()
        if self.tok==Lexer.TOK_IDENT:
            a=self.lex.data
            self._next()
            if self.tok==Lexer.TOK_CMP and self.lex.data=="=":
                self._next()
                out=(a, self.lex.data)
                self._next()
            else: raise Exception("'=' expected in affectation")
        else: raise Exception("IDENT expected in affectation")
        return out


    def _expr(self):
        if self.tok==Lexer.TOK_IDENT and self.lex.data=="select":
            return self._select()
        return self._exprOr()

    def _select(self, forecSelect=True):
        select=[]
        expr=None
        order=[]
        if self.tok==Lexer.TOK_IDENT and self.lex.current=="select":
            self._next()

            if self.tok==Lexer.TOK_MUL:
                self._next()
                if self.lex.data == "where":
                    self._next()
                else: raise Exception("Where expected after select statement")
            else:
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
        else: raise Exception("select expected")

        expr=self._exprOr()

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

        return SelectExpr(select, expr, order)

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
                raise Exception("Parenthese fermante manquante=> " + Lexer.tokstr(self.tok)+ "'"+str(self.lex.data)+"'")
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
            if self.tok==Lexer.TOK_PO:
                name=x
                params=self._tuple()
                return FunctionCall(name, params.first)
            return VarExpr(x, self.data)
        raise Exception("Attendu: int, float ou '(' => " + Lexer.tokstr(self.tok))

    def _tuple(self):
        if self.tok != Lexer.TOK_PO: raise Exception("'(' expected")
        self._next()
        x = []

        if self.tok == Lexer.TOK_PF:
            self._next()
            return TupleExpr(x)

        x.append(self._expr())

        while self.tok == Lexer.TOK_VIRGULE:
            self._next()
            x.append(self._expr())

        if self.tok != Lexer.TOK_PF: raise Exception("Array must end with ')'")
        self._next()
        return TupleExpr(x)

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

