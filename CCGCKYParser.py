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

    def __str__(this):
        return this.show()

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
        xxx = " " * (wdt - ldn + 1 - max(0, int((wdt - ldn)/ 2)))
        return f"{center(wdt, lup)}{up}\n{rep}{this.name}\n{center(wdt, ldn)}{down}{xxx}"

    def match(this, data):
        sigma = {}
        for (pat, dat) in zip(this.hyps, data):
            if not pat.match(dat, sigma):
                return None
        sem = None
        if this.sem:
            sem = (this.sem)(data)
        return this.concl.replace(sigma).deriving(this, sigma, data, sum([d.weight for d in data]), sem)

    def replace(this, sigma):
        return Inference(this.name, [h.replace(sigma) for h in this.hyps], this.concl.replace(sigma), this.sem)

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
    ),
    lambda data: data[1].sem.apply(data[0].sem) if data[0].sem and data[1].sem else None
)

ApplicationRight = Inference(">",
    [
        Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Y"))),
        Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
    ],
    Judgement(
        CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
        CCGTypeVar("X")
    ),
    lambda data: data[0].sem.apply(data[1].sem) if data[0].sem and data[1].sem else None
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

    return cache[f"{0}:{l - 1}"]







