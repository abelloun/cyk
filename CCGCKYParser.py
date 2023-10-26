from RDParser import RDParser as rd
from CCGrammar import Judgement, CCGExprVar, CCGTypeVar, CCGTypeAtomicVar, CCGTypeAtomic, CCGTypeComposite, CCGExprConcat, LambdaTermApplication, LambdaTermLambda, LambdaTermVar
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
            #print(pat.type, dat.type, sigma)
            if not pat.match(dat, sigma):
                return None
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

TypeRaisingRight = Inference("T<",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
    Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X")))),
    lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
    lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
)

TypeRaisingLeft = Inference("T>",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
    Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeVar("X")))),
    lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
    lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
)


####################################
## CCG CKY Parser
####################################
def CCGCKYParser(ccg, input_string, use_typer=False):
    combinators = [ApplicationLeft, ApplicationRight, CompositionLeft, CompositionRight]
    tokens = input_string.strip().split()
    num_tokens = len(tokens)
    chart = {}
    cache = {}

    # Reconnaisance des symboles terminaux
    for i, token in enumerate(tokens):
        if token not in ccg.rules:
            raise Exception(f"Token not found: \"{token}\"")

        chart[f"{i}:{i+1}"] = set([elem for elem in ccg.rules[token]])


    def add_combinations(combinator, left, right, current_chart, cache):
        if (left.type, right.type) not in cache:
            result = combinator.match([left, right])
            if result:
                current_chart.add(result)
                cache[(left.type, right.type)] = result
        return current_chart

    for span in range(2, num_tokens + 1):
        for start in range(0, num_tokens - span + 1):
            end = start + span
            chart[f"{start}:{end}"] = set()
            for step in range(1, span):
                mid = start + step
                for left in chart[f"{start}:{mid}"]:

                    new_left = TypeRaisingLeft.match([left]) if use_typer else None

                    for right in chart[f"{mid}:{end}"]:

                        current_chart = chart[f"{start}:{end}"]
                        new_right = TypeRaisingRight.match([right]) if use_typer else None

                        for combinator in combinators:
                            current_chart = add_combinations(combinator, left, right, current_chart, cache)

                            if new_left:
                                current_chart = add_combinations(combinator, new_left, right, current_chart, cache)

                            if new_right:
                                current_chart = add_combinations(combinator, left, new_right, current_chart, cache)



    return chart[f"{0}:{num_tokens}"]
