from RDParser import RDParser as rd
from Grammar import Judgement, CCGExprVar, CCGTypeVar, CCGTypeComposite, CCGExprConcat

####################################
# Inference
####################################
class Inference:
	def __init__(this, name, hyps, concl, sem = None):
		this.name = name
		this.hyps = hyps
		this.concl = concl
		this.sem = sem

	def show(this):
		def center(w, l):
			return " " * max(0, int((w - l)/ 2))
		up = ""
		down = this.concl.show()
		for hyp in this.hyps:
			if len(up):
				up = up + ", "
			up = up + hyp.show()
		lup = len(up)
		ldn = len(down)
		wdt = max(ldn, lup)
		rep = "-" * wdt
		return f"{center(wdt, lup)}{up}\n{rep}{this.name}\n{center(wdt, ldn)}{down}"

####################################
# Concrete Inferences
####################################
ApplicationLeft = Inference("<",
	[
		Judgement(CCGExprVar("b"), CCGTypeVar("Y")),
		Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y")))
	],
	Judgement(
		CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")),
		CCGTypeVar("X")
	)
)

ApplicationRight = Inference(">",
	[
		Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Y"))),
		Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
	],
	Judgement(
		CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
		CCGTypeVar("X")
	)
)

ComposeLeft = Inference("B<",
	[
		Judgement(CCGExprVar("b"), CCGTypeComposite(0, CCGTypeVar("Y"), CCGTypeVar("Z"))),
		Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y"))),
	],
	Judgement(
		CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")),
		CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Z"))
	)
)

ComposeRight = Inference("B>",
	[
		Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Y"))),
		Judgement(CCGExprVar("b"), CCGTypeComposite(1, CCGTypeVar("Y"), CCGTypeVar("Z"))),
	],
	Judgement(
		CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
		CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Z"))
	)
)

TypeRaisingLeft = Inference("T<",
	[Judgement(CCGExprVar("a"), CCGTypeVar("X"))],
	Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X"))))
)

TypeRaisingRight = Inference("T>",
	[Judgement(CCGExprVar("a"), CCGTypeVar("X"))],
	Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeVar("X"))))
)




for inf in [ApplicationLeft, ApplicationRight, ComposeLeft, ComposeRight, TypeRaisingLeft, TypeRaisingRight]:
	print("\n")
	print(inf.show())
	print("\n")



IgnoreParser = rd.seq(rd.rgx("( |\t)+"))
HelloParser = rd.lst(rd.alt(rd.str("Hello World !"), rd.str("Hello You !")))
print(HelloParser("  Hello World !  Hello World !Hello World !            			Hello World ! Hello You !", {}, IgnoreParser))
