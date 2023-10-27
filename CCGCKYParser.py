from RDParser import RDParser as rd
from CCGrammar import Judgement, CCGExprVar, CCGTypeVar, CCGTypeAtomicVar, CCGTypeAtomic, CCGTypeComposite, CCGExprConcat, LambdaTermApplication, LambdaTermLambda, LambdaTermVar
from functools import reduce
from collections import defaultdict
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
        return concl.replace(sigma).deriving(this, sigma, data, sem)

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



def add_combinations(combinators, left, right, current_chart):
    for combinator in combinators:
        result = combinator.match([left, right])
        if result:
            current_chart.add(result)
    return current_chart

def compute_chart(combinators, chart, span, start, use_typer=False):
    current_chart = set()
    for step in range(1, span):
        mid = start + step
        left_right_pairs = [(left, right) for left in chart[(start, mid)] for right in chart[(mid, start + span)]]

        for left, right in left_right_pairs:
            current_chart = add_combinations(combinators, left, right, current_chart)
            if use_typer:
                new_right = TypeRaisingRight.match([right])
                if new_right:
                    current_chart = add_combinations(combinators, left, new_right, current_chart)
            if use_typer:
                new_left = TypeRaisingLeft.match([left])
                if new_left:
                    current_chart = add_combinations(combinators, new_left, right, current_chart)

    return current_chart

def reconstruct(parses):
    result = []
    for parse in parses:
        for deriv in parse.derivation:

            if deriv["derivation"]:
                past = reconstruct(deriv["derivation"][2])
                for subpast in past:
                    result.append(subpast + [parse])
            else:
                result.append([parse])
    #print(result)
    return result



####################################
## CCG CKY Parser
####################################
def CCGCKYParser(ccg, input_string, use_typer=False):
    tokens = input_string.strip().split()
    num_tokens = len(tokens)
    chart = {}
    combinators = {ApplicationLeft, ApplicationRight, CompositionLeft, CompositionRight}
    # Reconnaisance des symboles terminaux
    for i, token in enumerate(tokens):
        if token not in ccg.rules:
            raise Exception(f"Token not found: \"{token}\"")

        chart[(i, i+1)] = set(ccg.rules[token])

    for span in range(2, num_tokens + 1):
        for start in range(0, num_tokens - span + 1):
            chart[(start, start + span)] = compute_chart(combinators, chart, span, start, use_typer)

    return [elem for elem in chart[(0, num_tokens)] if elem.type.show() == ccg.terminal]
