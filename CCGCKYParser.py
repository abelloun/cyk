from RDParser import RDParser as rd
from CCGrammar import Judgement, CCGExprVar, CCGTypeVar, CCGTypeAtomicVar, CCGTypeComposite, CCGExprConcat, LambdaTermApplication, LambdaTermLambda, LambdaTermVar
from functools import reduce
####################################
## Inference Class
####################################
class Inference:
    def __init__(this, name, hyps, concl, sem = None, helper = None):
        this.name = name
        this.hyps = hyps
        this.concl = concl
        this.sem = sem
        this.helper = helper if helper else lambda x: x

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
        hyps, concl = this.helper((this.hyps, this.concl))
        for (pat, dat) in zip(hyps, data):
            pat = pat.replace(sigma)
            dat = dat.replace(sigma)
            if not pat.match(dat, sigma):
                return None
            #~ print(f"ok")
            #~ print([f"{k}: {sigma[k].show()}" for k in sigma])
        sem = None
        if this.sem:
            sem = (this.sem)(data)
        return concl.replace(sigma).deriving(this, sigma, data, sum([d.weight for d in data]), sem)

    def replace(this, sigma):
        return Inference(this.name, [h.replace(sigma) for h in this.hyps], this.concl.replace(sigma), this.sem)

####################################
## Concrete Inferences Rules (aka Combinators)
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
    ),
    lambda data: LambdaTermLambda("x", LambdaTermApplication(data[1].sem, LambdaTermApplication(data[0].sem, LambdaTermVar("x")))) if data[0].sem and data[1].sem else None
)

CompositionRight = Inference("B>",
    [
        Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Y"))),
        Judgement(CCGExprVar("b"), CCGTypeComposite(1, CCGTypeVar("Y"), CCGTypeVar("Z"))),
    ],
    Judgement(
        CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
        CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Z"))
    ),
    lambda data: LambdaTermLambda("x", LambdaTermApplication(data[0].sem, LambdaTermApplication(data[1].sem, LambdaTermVar("x")))) if data[0].sem and data[1].sem else None
)

TypeRaisingLeft = Inference("T<",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
    Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X")))),
    lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
    lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
)

TypeRaisingRight = Inference("T>",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
    Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeVar("X")))),
    lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
    lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
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

    # Terminal symbols recognition
    for i in range(l):
        if stream[i] not in ccg.rules:
            raise Exception(f"Token not found \"{stream[i]}\"!")
        cache[f"{i}:{i}"] = ccg.rules[stream[i]]

    # Root Type raising application
    for k in cache:
        toadd = []
        for e in cache[k]:
            res = TypeRaisingLeft.match([e])
            if res: toadd.append(res)
            res = TypeRaisingRight.match([e])
            if res: toadd.append(res)
        cache[k] += toadd

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

            # Type raising application
            if j != (l - 1):
                toadd = []
                for e in cache[f"{s}:{j}"]:
                    res = TypeRaisingLeft.match([e])
                    if res: toadd.append(res)
                    res = TypeRaisingRight.match([e])
                    if res: toadd.append(res)
                cache[f"{s}:{j}"] += toadd

    return cache[f"{0}:{l - 1}"]
