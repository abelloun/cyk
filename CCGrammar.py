from functools import reduce
from RDParser import RDParser as rd

################################################
## Some basic definitions
################################################

def sel(idx, parse):
    return rd.act(parse, lambda x: x[idx])

Identifier = rd.rgx("[a-zA-Zéèêà_][a-zA-Zéèêà_0-9]*")
Integer = rd.rgx("[0-9]+")
Spaces = rd.rgx("( |\t)+")

####################################
## Judgement ( CCGExpr => CCGType )
## Alias ( CCGType :: CCGType )
####################################
class Judgement:
    def __init__(this, expr, type, weight = 0, sem = None):
        this.expr = expr
        this.type = type
        this.weight = weight
        this.sem = sem
    def show(this):
        weight = f"({str(this.weight)})" if this.weight else ""
        sem = (" { %s }" % this.sem.show()) if this.sem else ""
        return f"{this.expr.show()}:{weight}{this.type.show()}{sem}"
    def subst(this, name, type):
        return Judgement(this.expr, this.type.subst(name, type), this.weight, this.sem)
    def match(this, data, sigma):
        if not this.expr.match(data.expr, sigma):
            return None
        if not this.type.match(data.type, sigma):
            return None
        return True
    def replace(this, sigma):
        return Judgement(this.expr.replace(sigma), this.type.replace(sigma), this.weight, this.sem)

class Alias:
    def __init__(this, alias, type):
        this.alias = alias
        this.type = type
    def show(this):
        return f"{this.alias} = {this.type.show()}"
    def subst(this, name, type):
        return Alias(this.alias, this.type.subst(name, type))


####################################
## CCG Expressions
####################################
class CCGExpr:
    pass

class CCGExprVar(CCGExpr):
    def __init__(this, name):
        this.name = name
    def __str__(this):
        return this.show()
    def show(this):
        return this.name
    def match(this, data, sigma):
        if this.name not in sigma:
            sigma[this.name] = data
            return True
        return sigma[this.name].match(data)
    def replace(this, sigma):
        return sigma[this.name] if this.name in sigma else this

class CCGExprString(CCGExpr):
    def __init__(this, str):
        this.str = str
    def __str__(this):
        return this.show()
    def show(this):
        return f"\"{this.str}\""

class CCGExprConcat(CCGExpr):
    def __init__(this, left, right):
        this.left = left
        this.right = right
    def __str__(this):
        return this.show()
    def show(this):
        return f"{this.left.show()} {this.right.show()}"
    def replace(this, sigma):
        return CCGExprConcat(this.left.replace(sigma), this.right.replace(sigma))

################################################
## CCG Types
################################################
class CCGType:
    pass

class CCGTypeVar(CCGType):
    def __init__(this, name):
        this.name = name
    def __str__(this):
        return this.show()
    def show(this):
        return f"${this.name}"
    def subst(this, name, type):
        return type if this.name == name else this
    def match(this, data, sigma):
        if this.name not in sigma:
            sigma[this.name] = data
            return True
        #~ return data.match(sigma[this.name], sigma)
        return sigma[this.name].match(data, sigma)
    def replace(this, sigma):
        return sigma[this.name] if this.name in sigma else this

class CCGTypeAtomic(CCGType):
    def __init__(this, name):
        this.name = name
    def __str__(this):
        return this.show()
    def show(this):
        return this.name
    def subst(this, name, type):
        return type if this.name == name else this
    def match(this, data, sigma):
        if isinstance(data, CCGTypeAnnotation):
            data = data.type
            #~ sys.exit()
        return isinstance(data, CCGTypeAtomic) and this.name == data.name

class CCGTypeComposite(CCGType):
    def __init__(this, dir, left, right):
        this.dir = dir
        this.left = left
        this.right = right
    def __str__(this):
        return this.show()
    def show(this):
        slash = "/" if this.dir else "\\"
        return f"({this.left.show()} {slash} {this.right.show()})"
    def subst(this, name, type):
        return CCGTypeComposite(this.dir, this.left.subst(name, type), this.right.subst(name, type))
    def match(this, data, sigma):
        if not isinstance(data, CCGTypeComposite) or this.dir != data.dir:
            return None
        return this.left.match(data.left, sigma) and this.right.match(data.right, sigma)
    def replace(this, sigma):
        return CCGTypeComposite(this.dir, this.left.replace(sigma), this.right.replace(sigma))

class CCGTypeAnnotation(CCGType):
    def __init__(this, type, annot):
        this.type = type
        this.annot = annot
    def __str__(this):
        return this.show()
    def show(this):
        return f"{this.type.show()}[{this.annot}]"
    def subst(this, name, type):
        return CCGTypeAnnotation(this.type.subst(name, type), this.annot)
    def match(this, data, sigma):
        if not isinstance(data, CCGTypeAnnotation):
            return this.type.match(data, sigma)
        #~ if this.annot == data.annot:
            #~ return this.type.match(data.type, sigma)
        return this.type.match(data.type, sigma)
        #~ return None


CCGTypeParser = rd.grow("type", lambda type: rd.alt(
    rd.act(rd.seq(type, rd.str("["), Identifier, rd.str("]")), lambda x: CCGTypeAnnotation(x[0], x[2])),
    rd.act(rd.seq(type, rd.alt(rd.str("\\"), rd.str("/")), type), lambda x: CCGTypeComposite(x[1] == '/', x[0], x[2])),
    rd.act(sel(1, rd.seq(rd.str("$"), rd.raw(Identifier))), CCGTypeVar),
    rd.act(rd.seq(rd.str("("), type, rd.str(")")), lambda x: x[1]),
    rd.act(Identifier, CCGTypeAtomic),
))

################################################
## Lambda Terms for the denotation
## and parser for lambda terms
################################################
class LambdaTerm:
    pass

class LambdaTermVar(LambdaTerm):
    def __init__(this, name):
        this.name = name
    def show(this):
        return this.name
    def replace(this, var, expr):
        if this.name == var:
            return expr
        return this

class LambdaTermBinop(LambdaTerm):
    def __init__(this, op, left, right):
        this.op = op
        this.left = left
        this.right = right
    def show(this):
        return f"({this.left.show()} {this.op} {this.right.show()})"
    def replace(this, var, expr):
        return LambdaTermBinop(this.op,
            this.left.replace(var, expr),
            this.right.replace(var, expr)
        )

class LambdaTermPredicate(LambdaTerm):
    def __init__(this, fun, args):
        this.fun = fun
        this.args = args
    def show(this):
        args = ", ".join([arg.show() for arg in this.args])
        return f"{this.fun.show()}({args})"
    def replace(this, var, expr):
        return LambdaTermPredicate(this.fun.replace(var, expr), [arg.replace(var, expr) for arg in this.args])

class LambdaTermApplication(LambdaTerm):
    def __init__(this, fun, arg):
        this.fun = fun
        this.arg = arg
    def show(this):
        return f"({this.fun.show()} {this.arg.show()})"
    def replace(this, var, expr):
        return LambdaTermPredicate(this.fun.replace(var, expr), this.arg.replace(var, expr))

def LambdaTermExistsR(u, v):
    return LambdaTermExists(v, u)

class LambdaTermExists(LambdaTerm):
    def __init__(this, var, body):
        this.var = var
        this.body = body
    def show(this):
        return f"(exists {this.var}. {this.body.show()})"
    def replace(this, var, expr):
        if this.var == var:
            return this
        return LambdaTermExists(this.var, this.body.replace(var, expr))
    def apply(this, arg):
        return this.body.replace(this.var, arg)

def LambdaTermLambdaR(u, v):
    return LambdaTermLambda(v, u)

class LambdaTermLambda(LambdaTerm):
    def __init__(this, var, body):
        this.var = var
        this.body = body
    def show(this):
        return f"(\\{this.var}. {this.body.show()})"
    def replace(this, var, expr):
        if this.var == var:
            return this
        return LambdaTermLambda(this.var, this.body.replace(var, expr))
    def apply(this, arg):
        return this.body.replace(this.var, arg)

LambdaTermParser = rd.grow('expr', lambda expr: rd.alt(
    rd.act(rd.seq(expr, rd.str(" "), expr), lambda x: LambdaTermApplication(x[0], x[2])),
    rd.act(rd.seq(expr, rd.raw(rd.str("(")), rd.lst(sel(0, rd.seq(expr, rd.mbe(rd.str(","))))), rd.str(")")), lambda x: LambdaTermPredicate(x[0], x[2])),
    rd.act(rd.seq(expr, rd.rgx("\+|\&|\|"), expr), lambda x: LambdaTermBinop(x[1], x[0], x[2])),
    rd.act(rd.seq(rd.str("\\"), rd.lst1(Identifier), rd.str("."), expr), lambda x: reduce(LambdaTermLambdaR, x[1], x[3])),
    rd.act(rd.seq(rd.str("exists"), rd.lst1(Identifier), rd.str("."), expr), lambda x: reduce(LambdaTermExistsR, x[1], x[3])),
    rd.act(rd.seq(rd.str("("), expr, rd.str(")")), lambda x: x[1]),
    rd.act(Identifier, LambdaTermVar)
))






################################################
## Grammar Parser
## This is not the CKY parser, instead it
## is for parsing the grammar rules for the CKY
################################################
class CCGrammar:
    newLines = rd.lst1(rd.str("\n"))
    axiom = sel(0, rd.seq(Identifier, rd.mbe(rd.str(","))))
    axioms = rd.act(rd.seq(rd.str(":-"), rd.lst1(axiom)), lambda x: {"axioms": x[1]})
    alias = rd.act(rd.seq(Identifier, rd.str("::"), CCGTypeParser), lambda x: {"alias": Alias(x[0], x[2])})
    weight = rd.alt(rd.act(rd.seq(rd.str("("), Integer, rd.str(")")), lambda x: int(x[1])), rd.val(0))
    lmbda = sel(1, rd.seq(rd.str("{"), LambdaTermParser, rd.str("}")))
    judgm = rd.act(
        rd.seq(rd.rgx("[^\s]+"), rd.str("=>"), weight, CCGTypeParser, rd.mbe(lmbda)),
        lambda x: {"judgm": Judgement(CCGExprString(x[0]), x[3], x[2], x[4])}
    )
    comment = rd.act(rd.seq(rd.str("#"), rd.rgx(".*")), lambda x: None)
    grammar = sel(0, rd.seq(rd.lst(sel(1, rd.seq(newLines, rd.alt(comment, axioms, alias, judgm)))), newLines, rd.end()))

    @classmethod
    def parse(self, str):
        res = self.grammar(str, {}, Spaces)
        if res:
            return res[0]
        raise Exception("Parse Error !")

    def __init__(this, strGram):
        this.axioms = {}
        this.aliases = {}
        this.rules = {}
        for stmt in this.parse(strGram):
            if stmt is None:
                pass
            elif "axioms" in stmt:
                for ax in stmt["axioms"]:
                    this.axioms[ax] = ax
            elif "alias" in stmt:
                this.aliases[stmt["alias"].alias] = stmt["alias"]
            elif "judgm" in stmt:
                if stmt["judgm"].expr.str not in this.rules:
                    this.rules[stmt["judgm"].expr.str] = []
                this.rules[stmt["judgm"].expr.str].append(stmt["judgm"])

        for (alk, alv) in this.aliases.items():
            for (elk, elv) in this.aliases.items():
                this.aliases[elk] = elv.subst(alv.alias, alv.type)
            for (rulk, rulvs) in this.rules.items():
                this.rules[rulk] = [r.subst(alv.alias, alv.type) for r in rulvs]

    def show(this):
        axioms = ":- " + ", ".join(this.axioms.keys())
        aliases = "\n".join([v.show() for v in this.aliases.values()])
        rules = "\n".join([f"{r.show()}" for rl in this.rules.values() for r in rl])
        return "\n".join([axioms, aliases, rules])

