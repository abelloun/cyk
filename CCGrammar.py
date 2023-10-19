from random import randint
from functools import reduce
from RDParser import RDParser as rd

################################################
## Some basic helper definitions
################################################
def sel(idx, parse):
    return rd.act(parse, lambda x: x[idx])

Identifier = rd.rgx("[a-zA-Zéèêà_][a-zA-Zéèêà_0-9]*")
Integer = rd.rgx("[0-9]+")
Spaces = rd.rgx("( |\t)+")


####################################
## CCG Expressions
## ( strings of terminals )
####################################
class CCGExpr:
    def __str__(this):
        return this.show()


class CCGExprVar(CCGExpr):
    def __init__(this, name):
        this.name = name
    def show(this):
        return this.name
    def replace(this, sigma):
        return sigma[this.name] if this.name in sigma else this
    def match(this, data, sigma):
        if this.name not in sigma:
            sigma[this.name] = data
            return True
        return sigma[this.name].match(data)


class CCGExprString(CCGExpr):
    def __init__(this, str):
        this.str = str
    def show(this):
        return f"\"{this.str}\""
    def replace(this, sigma):
        return this
    def match(this, data, sigma):
        if isinstance(data, CCGExprString):
            return this.str == data.str


class CCGExprConcat(CCGExpr):
    def __init__(this, left, right):
        this.left = left
        this.right = right
    def show(this):
        return f"{this.left.show()} {this.right.show()}"
    def replace(this, sigma):
        return CCGExprConcat(this.left.replace(sigma), this.right.replace(sigma))
    def match(this, data, sigma):
        raise Exception("Can't match a concatenation expr !")


################################################
## CCG Types
################################################
class CCGType:
    def __str__(this):
        return this.show()


class CCGTypeVar(CCGType):
    def __init__(this, name):
        this.name = name
    def show(this):
        return f"${this.name}"
    def expand(this, name, type):
        return type if this.name == name else this
    def replace(this, sigma):
        return sigma[this.name] if this.name in sigma else this
    def match(this, data, sigma):
        if this.name not in sigma:
            sigma[this.name] = data
            return True
        return sigma[this.name].match(data, sigma)


class CCGTypeAtomicVar(CCGType):
    def __init__(this, name):
        this.name = name
    def show(this):
        return f"@{this.name}"
    def expand(this, name, type):
        return type if this.name == name else this
    def replace(this, sigma):
        return sigma[this.name] if this.name in sigma else this
    def match(this, data, sigma):
        if not isinstance(data, CCGTypeAtomic):
            return False
        if (this.name not in sigma):
            sigma[this.name] = data
            return True
        return sigma[this.name].match(data, sigma)


class CCGTypeAtomic(CCGType):
    def __init__(this, name):
        this.name = name
    def show(this):
        return this.name
    def expand(this, name, type):
        return type if this.name == name else this
    def replace(this, sigma):
        return this
    def match(this, data, sigma):
        if isinstance(data, CCGTypeAnnotation):
            data = data.type
        return isinstance(data, CCGTypeAtomic) and this.name == data.name


class CCGTypeComposite(CCGType):
    def __init__(this, dir, left, right):
        this.dir = dir
        this.left = left
        this.right = right
    def show(this):
        slash = "/" if this.dir else "\\"
        return f"({this.left.show()} {slash} {this.right.show()})"
    def expand(this, name, type):
        return CCGTypeComposite(this.dir, this.left.expand(name, type), this.right.expand(name, type))
    def replace(this, sigma):
        return CCGTypeComposite(this.dir, this.left.replace(sigma), this.right.replace(sigma))
    def match(this, data, sigma):
        if not isinstance(data, CCGTypeComposite) or this.dir != data.dir:
            return False
        return this.left.match(data.left, sigma) and this.right.match(data.right, sigma)


class CCGTypeAnnotation(CCGType):
    def __init__(this, type, annot):
        this.type = type
        this.annot = annot
    def show(this):
        return f"{this.type.show()}[{this.annot}]"
    def expand(this, name, type):
        return CCGTypeAnnotation(this.type.expand(name, type), this.annot)
    def replace(this, sigma):
        return CCGTypeAnnotation(this.type.replace(sigma), this.annot)
    def match(this, data, sigma):
        if not isinstance(data, CCGTypeAnnotation):
            return this.type.match(data, sigma)
        if this.annot == data.annot:
            return this.type.match(data.type, sigma)
        return False


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
    count = -1
    def __str__(this):
        return this.show()
    @classmethod
    def fresh(self, var):
        self.count += 1
        return f"{var.split('_')[0]}_{self.count}"


class LambdaTermVar(LambdaTerm):
    def __init__(this, name):
        this.name = name
    def show(this):
        return this.name
    def eval(this, env):
        return env[this.name] if this.name in env else this
    def apply(this, arg):
        return LambdaTermApplication(this, arg)
    def applyPredicate(this, args):
        return LambdaTermPredicate(this, args)


class LambdaTermBinop(LambdaTerm):
    def __init__(this, op, left, right):
        this.op = op
        this.left = left
        this.right = right
    def show(this):
        return f"({this.left.show()} {this.op} {this.right.show()})"
    def eval(this, env):
        return LambdaTermBinop(this.op, this.left.eval(env), this.right.eval(env))
    def apply(this, arg):
        return LambdaTermBinop(this.op, this.left.apply(arg), this.right.apply(arg))
    def applyPredicate(this, args):
        return LambdaTermBinop(this.op, this.left.applyPredicate(args), this.right.applyPredicate(args))


class LambdaTermPredicate(LambdaTerm):
    def __init__(this, fun, args):
        this.fun = fun
        this.args = args
    def show(this):
        args = ", ".join([arg.show() for arg in this.args])
        return f"{this.fun.show()}({args})"
    def eval(this, env):
        return this.fun.eval(env).applyPredicate([arg.eval(env) for arg in this.args])
    def apply(this, arg):
        return LambdaTermPredicate(this.fun, this.args + [arg])
    def applyPredicate(this, args):
        return LambdaTermPredicate(this.fun, this.args + args)


class LambdaTermApplication(LambdaTerm):
    def __init__(this, fun, arg):
        this.fun = fun
        this.arg = arg
    def show(this):
        return f"({this.fun.show()} {this.arg.show()})"
    def eval(this, env):
        return this.fun.eval(env).apply(this.arg.eval(env))
    def apply(this, arg):
        return LambdaTermApplication(this, arg)
    def applyPredicate(this, args):
        return LambdaTermPredicate(this, args)


class LambdaTermLambda(LambdaTerm):
    @classmethod
    def build(self, u, v):
        return self(v, u)
    def __init__(this, var, body):
        this.var = var
        this.body = body
    def show(this):
        return f"(\\{this.var}. {this.body.show()})"
    def eval(this, env):
        v = this.fresh(this.var)
        return LambdaTermLambda(v, this.body.eval({**env, this.var: LambdaTermVar(v)}))
    def apply(this, arg):
        return this.body.eval({this.var: arg})
    def applyPredicate(this, args):
        f = this.body.eval({this.var: args[0]})
        return f.applyPredicate(args[1:]) if len(args) > 1 else f


class LambdaTermExists(LambdaTerm):
    @classmethod
    def build(self, u, v):
        return self(v, u)
    def __init__(this, var, body):
        this.var = var
        this.body = body
    def show(this):
        return f"(exists {this.var}. {this.body.show()})"
    def eval(this, env):
        v = this.fresh(this.var)
        return LambdaTermExists(v, this.body.eval({**env, this.var: LambdaTermVar(v)}))
    def apply(this, arg):
        return this.body.eval({this.var: arg})
    def applyPredicate(this, args):
        f = this.body.eval({this.var: args[0]})
        return f.applyPredicate(args[1:]) if len(args) > 1 else f


LambdaTermParser = rd.grow('expr', lambda expr: rd.alt(
    rd.act(rd.seq(expr, rd.str(" "), expr), lambda x: LambdaTermApplication(x[0], x[2])),
    rd.act(rd.seq(expr, rd.rgx("\+|\&|\|"), expr), lambda x: LambdaTermBinop(x[1], x[0], x[2])),
    rd.act(rd.seq(Identifier, rd.raw(rd.str("(")), rd.lst(sel(0, rd.seq(expr, rd.mbe(rd.str(","))))), rd.str(")")), lambda x: LambdaTermPredicate(LambdaTermVar(x[0]), x[2])),
    rd.act(rd.seq(rd.str("\\"), rd.act(rd.lst1(Identifier), lambda x: [x.reverse(), x][1]), rd.str("."), expr), lambda x: reduce(LambdaTermLambda.build, x[1], x[3])),
    rd.act(rd.seq(rd.str("exists"), rd.rgx("\s+"), rd.lst1(Identifier), rd.str("."), expr), lambda x: reduce(LambdaTermExists.build, x[2], x[4])),
    rd.act(rd.seq(rd.str("("), expr, rd.str(")")), lambda x: x[1]),
    rd.act(Identifier, LambdaTermVar)
))


####################################
## Judgement ( CCGExpr => CCGType )
####################################
class Judgement:
    def __init__(this, expr, type, weight = 0, sem = None, derivation = None):
        this.expr = expr
        this.type = type
        this.weight = weight
        this.sem = sem
        this.derivation = derivation
    def show(this):
        weight = f" (weight: {str(this.weight)}) " if this.weight else ""
        sem = (" { %s }" % this.sem.show()) if this.sem else ""
        return f"{this.expr.show()}:{weight}{this.type.show()}{sem}"
    def expand(this, name, type):
        return Judgement(this.expr, this.type.expand(name, type), this.weight, this.sem, this.derivation)
    def match(this, data, sigma):
        if not this.expr.match(data.expr, sigma):
            return None
        if not this.type.match(data.type, sigma):
            return None
        return True
    def replace(this, sigma):
        return Judgement(this.expr.replace(sigma), this.type.replace(sigma), this.weight, this.sem, this.derivation)
    def deriving(this, combinator, sigma, judmts, weight, sem = None):
        this.derivation = [combinator, sigma, judmts]
        this.sem = sem
        this.weight = weight
        return this


####################################
## Alias ( CCGType :: CCGType )
####################################
class Alias:
    def __init__(this, key, value):
        this.key = key
        this.value = value
    def show(this):
        return f"{this.key} = {this.value.show()}"
    def expand(this, key, value):
        return Alias(this.key, this.value.expand(key, value))


################################################
## Grammar (Parser + Constructor + Printer)
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
                this.aliases[stmt["alias"].key] = stmt["alias"]
            elif "judgm" in stmt:
                if stmt["judgm"].expr.str not in this.rules:
                    this.rules[stmt["judgm"].expr.str] = []
                this.rules[stmt["judgm"].expr.str].append(stmt["judgm"])

        for (alk, alv) in this.aliases.items():
            for (elk, elv) in this.aliases.items():
                this.aliases[elk] = elv.expand(alv.key, alv.value)
            for (rulk, rulvs) in this.rules.items():
                this.rules[rulk] = [r.expand(alv.key, alv.value) for r in rulvs]

        #~ print(this.show() + "\n\n\n")

    def show(this):
        axioms = ":- " + ", ".join(this.axioms.keys())
        aliases = "\n".join([v.show() for v in this.aliases.values()])
        rules = "\n".join([f"{r.show()}" for rl in this.rules.values() for r in rl])
        return "\n".join([axioms, aliases, rules])

