from RDParser import RDParser as rd

################################################
## Some basic definitions
################################################

def sel(idx, parse):
	return rd.act(parse, lambda x: x[idx])

Identifier = rd.rgx("[a-zA-Z_][a-zA-Z_0-9]*")
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

class Alias:
	def __init__(this, alias, type):
		this.alias = alias
		this.type = type
	def show(this):
		return f"{this.alias} = {this.type.show()}"


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

class CCGTypeAtomic(CCGType):
	def __init__(this, name):
		this.name = name
	def __str__(this):
		return this.show()
	def show(this):
		return this.name

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

class CCGTypeAnnotation(CCGType):
	def __init__(this, type, annot):
		this.type = type
		this.annot = annot
	def __str__(this):
		return this.show()
	def show(this):
		return f"{this.type.show()}[{this.annot}]"


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

class LambdaTermLambda(LambdaTerm):
	def __init__(this, var, body):
		this.var = var
		this.body = body
	def show(this):
		return f"(\\{this.var}-> {this.body.show()})"
	def replace(this, var, expr):
		if this.var == var:
			return this
		return LambdaTermLambda(this.var, this.body.replace(var, expr))
	def apply(this, arg):
		return this.body.replace(this.var, arg)

LambdaTermParser = rd.grow('expr', lambda expr: rd.alt(
	rd.act(rd.seq(expr, rd.rgx("\+|\&|\|"), expr), lambda x: LambdaTermBinop(x[1], x[0], x[2])),
	rd.act(rd.seq(rd.str("\\"), Identifier, rd.str("->"), expr), lambda x: LambdaTermLambda(x[1], x[3])),
	rd.act(rd.seq(rd.str("("), expr, rd.str(")")), lambda x: x[1]),
	rd.act(Identifier, LambdaTermVar)
))






################################################
## Grammar Parser
## This is not the CKY parser, instead it
## is for parsing the grammar rules for the CKY
################################################
def GParser():

	NewLines = rd.lst1(rd.str("\n"))

	Axiom = sel(0, rd.seq(Identifier, rd.mbe(rd.str(","))))
	Axioms = rd.act(rd.seq(rd.str(":-"), rd.lst1(Axiom)), lambda x: {"axioms": x[1]})
	PAlias = rd.act(rd.seq(Identifier, rd.str("::"), CCGTypeParser), lambda x: {"alias": {x[0]: Alias(x[0], x[2])}})
	Weight = rd.alt(rd.act(rd.seq(rd.str("("), Integer, rd.str(")")), lambda x: int(x[1])), rd.val(0))
	Lambda = sel(1, rd.seq(rd.str("{"), LambdaTermParser, rd.str("}")))
	Judgm = rd.act(
		rd.seq(rd.rgx("[^\s]+"), rd.str("=>"), Weight, CCGTypeParser, rd.mbe(Lambda)),
		lambda x: {"judgm": {x[0]: Judgement(CCGExprString(x[0]), x[3], x[2], x[4])}}
	)

	Grammar = sel(0, rd.seq(rd.lst(sel(1, rd.seq(NewLines, rd.alt(Axioms, PAlias, Judgm)))), NewLines, rd.end()))

	def parse(str):
		res = Grammar(str, {}, Spaces)
		if res:
			return res[0]
		raise Exception("Parse Error !")

	return parse



Grammar = '''
    :- Phrase, GrNom, Nom, VerbeSuj,
    :- VerbeInf, PhraseInterro, GrQuestion, Prop, PP
    DetMasc :: GrNom[Masc]/Nom[Masc]
    DetFem :: GrNom[Fem]/Nom[Fem]
    DetMascPlur :: GrNom[MascPlur]/Nom[MascPlur]
    DetFemPlur :: GrNom[FemPlur]/Nom[FemPlur]
    AdjMascL :: Nom[Masc]/Nom[Masc]
    AdjFemL :: Nom[Fem]/Nom[Fem]
    AdjMascR :: Nom[Masc]\\Nom[Masc]

    la => AnteposMasc
    le => AnteposMasc
    la => AnteposFem
    le => AnteposFem

    donné => AdjMascL
    méchant => AdjMascL
    mangée => AdjFemL
    noir => AdjMascR

    très =>(100) AdjMascL/AdjMascL
    très =>(100) AdjFemL/AdjFemL
    très =>(100) AdjMascR/AdjMascR
    très =>(100) AdjFemR/AdjFemR

    Il =>(100) Phrase/VbIntransM { \\x -> x }
    Elle =>(100) Phrase/VbIntransF

'''



print(LambdaTermLambda("x", LambdaTermBinop("+", LambdaTermVar("x"), LambdaTermVar("x"))).show())
print(LambdaTermParser(" \\ x -> x + x + x ", {}, Spaces)[0].apply(LambdaTermVar("y")).show())
print(CCGTypeParser("(Hello\\Bye)[Annot]/Type[Annot2]", {}, Spaces)[0].show())

print("")
xs = GParser()(Grammar)
for x in xs:
	if "axioms" in x:
		print("axioms : " + str(x["axioms"]))
	elif "alias" in x:
		print("alias  : " + list(x["alias"].items())[0][1].show())
	elif "judgm" in x:
		print("judgm  : " + str(list(x["judgm"].items())[0][1].show()))






