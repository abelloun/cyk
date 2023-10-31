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

class CKYDerivation:
    def __init__(this, current, past, combinator):
        this.current = current
        this.past = past
        this.combinator = combinator

    def __str__(this):
        return this.show()

    def sub_show(this, sem=False):
        if not this.past:
            current_show = this.current.type.show()
            current_expr = this.current.expr.show()
            if sem:
                current_sem = this.current.sem.show()
                offset = max(len(current_show), len(current_sem), len(current_expr))
                return ((offset-len(current_expr))//2)*" " + current_expr + "\n" + ((offset-len(current_show))//2)*" " + current_show + "\n" + ((offset-len(current_sem))//2)*" " + current_sem, offset
            else:
                offset = max(len(current_show), len(current_expr))
                return ((offset-len(current_expr))//2)*" " + current_expr + "\n" + ((offset-len(current_show))//2)*" " + current_show, offset

        if len(this.past) == 1:
            current_show = this.current.type.show()
            comb = this.combinator.name
            top, size = this.past[0].sub_show(sem)

            if sem:
                current_sem = this.current.sem.show()
                offset = max(len(current_show), len(current_sem), size)
                ntop = top.split("\n")
                res = ""
                for step in ntop:
                    res += ((offset-size)//2)*" " + step + "\n"
                return res + offset*"=" + comb + "\n" + ((offset-len(current_show))//2)*" "+ current_show + "\n"  + ((offset-len(current_sem))//2)*" " + current_sem, offset
            else:
                offset = max(len(current_show), size)
                ntop = top.split("\n")
                res = ""
                for step in ntop:
                    res += ((offset-size)//2)*" " + step + "\n"
                return res + offset*"=" + comb + "\n" + ((offset-len(current_show))//2)*" "+ current_show, offset

        if len(this.past) == 2:
            topl, sizel = this.past[0].sub_show(sem)
            topr, sizer = this.past[1].sub_show(sem)
            totsize = sizel+sizer+3
            toplm = topl.split("\n")
            toprm = topr.split("\n")
            current_show = this.current.type.show()

            comb = this.combinator.name
            if sem:
                current_sem = this.current.sem.show()
                offset = max(len(current_show), len(current_sem), totsize)
            else:
                offset = max(len(current_show), totsize)

            s = (offset-totsize)//2
            res = ""
            while len(toplm) > len(toprm):
                v = toplm.pop(0)
                res += s*" " + v + "\n"
            while len(toplm) < len(toprm):
                v = toprm.pop(0)
                res += s*" " + (sizel+3)*" " + v + "\n"

            while toplm:
                vl = toplm.pop(0)
                vd = toprm.pop(0)
                res += s*" " + vl + (sizel-len(vl)+3)*" " + vd + "\n"

            if sem:
                return res + offset*"=" + comb + "\n" + ((offset-len(current_show))//2)*" "+ current_show + "\n" + ((offset-len(current_sem))//2)*" "+ current_sem, offset
            else:
                return res + offset*"=" + comb + "\n" + ((offset-len(current_show))//2)*" "+ current_show, offset

    def show(this, sem=False):
        return this.sub_show(sem=sem)[0]

def reconstruct(parses):
    result = []
    for parse in parses:
        for deriv in parse.derivation:
            if deriv["derivation"]:
                past = reconstruct(deriv["derivation"][2])
                result.append(CKYDerivation(parse, past, deriv["derivation"][0]))
            else:
                result.append(CKYDerivation(parse, None, None))
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

    return reconstruct([elem for elem in chart[(0, num_tokens)] if elem.type.show() == ccg.terminal])
