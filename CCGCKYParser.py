from RDParser import RDParser as rd
from CCGrammar import Judgement, CCGExprVar, CCGTypeVar, CCGTypeComposite, CCGExprConcat
from functools import reduce
####################################
## Inference Class
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

    def match(this, data):
        sigma = {}
        for (pat, dat) in zip(this.hyps, data):
            if not pat.match(dat, sigma):
                return None
        return this.concl.replace(sigma)

####################################
## Concrete Inferences Rules
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

CompositionLeft = Inference("B<",
    [
        Judgement(CCGExprVar("b"), CCGTypeComposite(0, CCGTypeVar("Y"), CCGTypeVar("Z"))),
        Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y"))),
    ],
    Judgement(
        CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")),
        CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Z"))
    )
)

CompositionRight = Inference("B>",
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


def mapShow(x):
    def concat(x, y):
        return x + y[1].show()
    return reduce(concat, x, "")

####################################
## CCG CKY Parser
####################################
def CCGCKYParser(ccg, str):
    combinators = [ApplicationLeft, ApplicationRight, CompositionLeft, CompositionRight]
    stream = str.strip().split()
    l = len(stream)
    passes = [{} for i in stream]
    cache = {}
    for i in range(l):
        if stream[i] not in ccg.rules:
            raise Exception(f"Token not found \"{stream[i]}\"!")
        #~ passes[0][f"{i}:{i}"] = ccg.rules[stream[i]]
        cache[f"{i}:{i}"] = ccg.rules[stream[i]]

    for w in range(1, l):
        for s in range(0, l - w):
            j = s + w
            cache[f"{s}:{j}"] = []
            for e in range(s, j):
                #~ print(f"{w} => ({s} : {j}) => {s}:{e}/{e+1}:{j} {str}")
                for c in combinators:
                    for left in cache[f"{s}:{e}"]:
                        for right in cache[f"{e+1}:{j}"]:
                            result = c.match([left, right])
                            if result:
                                cache[f"{s}:{j}"].append(result)

    #~ for (k, i) in cache.items():
        #~ for ii in i:
            #~ print(f"{k} => {ii.show()}")

    #~ print([mapShow(s) for s in passes[0]])

    if len(cache[f"{0}:{l - 1}"]):
        for i in cache[f"{0}:{l - 1}"]:
            print(i.show())
    else:
        print(f"############### ECHEC on ::: {str}")







