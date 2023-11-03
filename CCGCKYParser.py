"""
CCG Expressions

This module defines classes and functions for working with Combinatory
Categorial Grammar (CCG) expressions and parsing.
It provides classes for representing CCG expressions, inference rules,
and CKY derivations.

Classes:
- TokenError: Exception raised for errors related to unrecognized tokens in
              CCG parsing.
- Inference: Represents an inference rule in a logical system.
             An inference rule consists of a name, a list of hypotheses
             (premises), a conclusion, an optional semantic function,
             and an optional helper function.
             This class also provides methods for matching the rule with data
             and replacing variables using a substitution dictionary.
- CKYDerivation: Represents a derivation in the CKY parsing algorithm. This
                 class is used to construct parse trees and is part of the
                 CCG CKY parser.

Functions:
- CCGCKYParser: Parse a given input string using Combinatory Categorial Grammar
                (CCG) and CKY parsing. It takes a CCG grammar, an input string,
                and an optional flag to enable type-raising, and returns a list
                of reconstructed CKY derivations.
- compute_chart: Computes the chart of valid derivations for a given span of
                 input.
- reconstruct: Reconstructs CKY derivations from judgements.
- add_combinations : Add valid combinations of combinators to the current
                    chart.

Example:
>>> ccg = CCGGrammar(...)
>>> input_string = "John eats apples"
>>> use_typer = True
>>> result = CCGCKYParser(ccg, input_string, use_typer)
>>> print(result)
[CKYDerivation(parse1), CKYDerivation(parse2), ...]

Raises:
- TokenError: If a token in the input string is not recognized in the
              CCG grammar.
"""
from CCGrammar import Judgement
from CCGLambdas import LambdaTermVar, LambdaTermApplication, LambdaTermLambda
from CCGTypes import CCGTypeVar, CCGTypeComposite, CCGTypeAtomicVar
from CCGExprs import CCGExprVar, CCGExprConcat


class TokenError(Exception):
    """
    Exception raised for errors related to unrecognized tokens in CCG parsing.

    Attributes:
        token (str): The unrecognized token that triggered the error.
        message (str, optional): A custom error message
                                (default is "Token not found: {token}").
    """

    def __init__(self, token, message="Token not found: "):
        """
        Initialize a TokenError object.

        Args:
            token (str): The unrecognized token that triggered the error.
            message (str, optional): A custom error message
                                    (default is "Token not found: {token}").
        """
        self.token = token
        self.message = message + f"\"{token}\""
        super().__init__(self.message)


####################################
# Inference Class
####################################
class Inference:
    """
    Represents an inference rule in a logical system.

    An inference rule consists of a name, a list of hypotheses (premises),
    a conclusion, an optional semantic function, and an optional helper
    function.

    Args:
    - name (str): The name of the inference rule.
    - hyps (list): A list of hypotheses, which are CCG expressions.
    - concl (CCGExpr): The conclusion, a CCG expression.
    - sem (function, optional): A semantic function for the inference.
    - helper (function, optional): A helper function for special processing of
                                    hypotheses and conclusions.

    Methods:
    - __str__(): Returns a string representation of the inference rule.
    - show(): Returns a formatted string representation of the inference rule.
    - match(data): Matches the inference rule with given data, updating
                    variable substitutions.
    - replace(sigma): Replaces variables in the inference rule using a
                        substitution dictionary.

    Example:
    >>> hyp1 = CCGExprVar("X")
    >>> hyp2 = CCGExprString("apple")
    >>> concl = CCGExprVar("Y")
    >>> inference = Inference("Example Rule", [hyp1, hyp2], concl,
                                sem=some_semantic_function)
    >>> print(inference)
    [ X, "apple" ] -- Example Rule --> Y
    """

    def __init__(self, name, hyps, concl, sem=None, helper=None):
        """
        Initialize an inference rule with a name, hypotheses, a conclusion,
        and optional functions.

        Args:
        - name (str): The name of the inference rule.
        - hyps (list): A list of hypotheses, which are CCG expressions.
        - concl (CCGExpr): The conclusion, a CCG expression.
        - sem (function, optional): A semantic function for the inference.
        - helper (function, optional): A helper function for special processing
                                        of hypotheses and conclusions.

        Example:
        >>> hyp1 = CCGExprVar("X")
        >>> hyp2 = CCGExprString("apple")
        >>> concl = CCGExprVar("Y")
        >>> inference = Inference("Example Rule", [hyp1, hyp2], concl)
        """
        self.name = name
        self.hyps = hyps
        self.concl = concl
        self.sem = sem
        self.helper = helper if helper else lambda x: x

    def __str__(self):
        """
        Returns a string representation of the inference rule.

        Returns:
        str: A string representation of the inference rule.

        Example:
        >>> print(inference)
        [ X, "apple" ] -- Example Rule --> Y
        """
        return self.show()

    def show(self):
        """
        Returns a formatted string representation of the inference rule.

        Returns:
        str: A formatted string representation of the inference rule.

        Example:
        >>> inference = Inference("Example Rule", [hyp1, hyp2], concl)
        >>> print(inference.show())
        [ X, "apple" ] -- Example Rule --> Y
        """

        def center(width, length):
            """
            Center a string within a given width.

            Args:
            - wwidth (int): The width to center within.
            - length (int): The length of the string to be centered.

            Returns:
            str: A string of spaces for centering.

            Example:
            >>> centered = center(10, 5)
            >>> print("|" + centered + "text" + centered + "|")
            |   text   |
            """
            return " " * max(0, (width - length)//2)

        up = ""
        down = self.concl.show()
        for hyp in self.hyps:
            if up:
                up = up + ", "
            up = up + hyp.show()
        lup = len(up)
        ldn = len(down)
        wdt = max(ldn, lup)
        rep = "-" * wdt
        xxx = " " * (wdt - ldn + 1 - max(0, (wdt - ldn)//2))
        name = self.name
        ctr = center(wdt, ldn)
        return f"{center(wdt, lup)}{up}\n{rep}{name}\n{ctr}{down}{xxx}"

    def match(self, data):
        """
        Matches the inference rule with given data, updating variable
        substitutions.

        Args:
        - data (list): A list of CCG expressions to match with the hypotheses.

        Returns:
        InferenceResult or None: An InferenceResult object if the data matches
                                the inference rule, or None if there is no
                                match.

        Example:
        >>> data = [CCGExprVar("X"), CCGExprString("apple")]
        >>> result = inference.match(data)
        """
        sigma = {}
        hyps, concl = self.helper((self.hyps, self.concl))
        for (pat, dat) in zip(hyps, data):
            pat = pat.replace(sigma)
            dat = dat.replace(sigma)
            if not pat.match(dat, sigma):
                return None
        sem = None
        if self.sem:
            sem = (self.sem)(data)
        return concl.replace(sigma).deriving(self, sigma, data, sem)

    def replace(self, sigma):
        """
        Replaces variables in the inference rule using a substitution
        dictionary.

        Args:
        - sigma (dict): A dictionary of variable substitutions.

        Returns:
        Inference: A new Inference object with variables replaced using the
                    given substitution.

        Example:
        >>> substitution = {"X": CCGExprString("fruit")}
        >>> new_inference = inference.replace(substitution)
        """
        hyps_rep = [h.replace(sigma) for h in self.hyps]
        concl_rep = self.concl.replace(sigma)
        return Inference(self.name, hyps_rep, concl_rep, self.sem)


####################################
# Concrete Inferences Rules (aka Combinators)
####################################
# """
# ApplicationLeft Combinator.
#
# self combinator applies the '<' operator for CCG expressions, which
# represents a left application operation in Combinatory Categorial
# Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'b' with type 'Y' and judgement of 'a' with type 'X/Y'.
# - Output: Judgement of 'b a' with type 'X'.
#
# Semantics:
# - Applies a semantic function to combine the semantics of 'a' and 'b' if they
# exist.
#
# Example:
# >>> app_left = ApplicationLeft.match([Judgement(CCGExprVar("b"),
#                                                 CCGTypeVar("Y")),
#     Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"),
#                                                    CCGTypeVar("Y"))])
# >>> print(app_left)
# Judgement(CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")), CCGTypeVar("X"))
# """
ApplicationLeft = Inference("<",
    [
        Judgement(CCGExprVar("b"), CCGTypeVar("Y")),
        Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"),
                                                       CCGTypeVar("Y")))
    ],
    Judgement(
        CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")),
        CCGTypeVar("X")
    ),
    lambda data: data[1].sem.apply(data[0].sem) if data[0].sem and data[1].sem else None
)


# """
# ApplicationRight Combinator.
#
# self combinator applies the '>' operator for CCG expressions, which represents
# a right application operation in Combinatory Categorial Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'a' with type 'X\Y' and judgement of 'b' with type 'Y'.
# - Output: Judgement of 'a b' with type 'X'.
#
# Semantics:
# - Applies a semantic function to combine the semantics of 'a' and 'b' if they exist.
#
# Example:
# >>> app_right = ApplicationRight.match([Judgement(CCGExprVar("a"),
#                                                   CCGTypeComposite(1, CCGTypeVar("X"),
#                                                                       CCGTypeVar("Y")),
#                                         Judgement(CCGExprVar("b"), CCGTypeVar("Y"))])
# >>> print(app_right)
# Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")), CCGTypeVar("X"))
# """
ApplicationRight = Inference(">",
    [
        Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"),
                                                       CCGTypeVar("Y"))),
        Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
    ],
    Judgement(
        CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
        CCGTypeVar("X")
    ),
    lambda data: data[0].sem.apply(data[1].sem) if data[0].sem and data[1].sem else None
)

# """
# CompositionLeft Combinator.
#
# self combinator applies the 'B<' operator for CCG expressions, which represents
# a left composition operation in Combinatory Categorial Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'b' with type 'Y/Z' and judgement of 'a' with type 'X/Y'.
# - Output: Judgement of 'b a' with type 'X/Z'.
#
# Semantics:
# - Applies a semantic function to combine the semantics of 'a' and 'b' if they exist.
#
# Example:
# >>> comp_left = CompositionLeft.match([Judgement(CCGExprVar("b"),
#                                                 CCGTypeComposite(0, CCGTypeVar("Y"), CCGTypeVar("Z")),
#                                        Judgement(CCGExprVar("a"),
#                                                 CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y"))])
# >>> print(comp_left)
# Judgement(CCGExprConcat(CCGExprVar("b"), CCGExprVar("a")),
#           CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Z"))
# """
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

# """
# CompositionRight Combinator.
#
# self combinator applies the 'B>' operator for CCG expressions, which represents
# a right composition operation in Combinatory Categorial Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'a' with type 'X\Y' and judgement of 'b' with type 'Y\Z'.
# - Output: Judgement of 'a b' with type 'X\Z'.
#
# Semantics:
# - Applies a semantic function to combine the semantics of 'a' and 'b' if they exist.
#
# Example:
# >>> comp_right = CompositionRight.match([Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"),
#                                                                                         CCGTypeVar("Y")),
#                                          Judgement(CCGExprVar("b"), CCGTypeComposite(1, CCGTypeVar("Y"),
#                                                                                         CCGTypeVar("Z"))])
# >>> print(comp_right)
# Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Z"))
# """
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

# """
# TypeRaisingRight Combinator.
#
# self combinator applies the 'T<' operator for CCG expressions, which represents
# a type raising operation in Combinatory Categorial Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'a' with a variable type 'X'.
# - Output: Judgement of 'a' with type 'T/(T/X)'.
#
# Semantics:
# - Raises the type 'X' to 'T' and applies a semantic function 'f' if it exists.
#
# Example:
# >>> tr_right = TypeRaisingRight.match([Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))])
# >>> print(tr_right)
# Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"),
#                                                 CCGTypeComposite(1, CCGTypeVar("T"),
#                                                                     CCGTypeVar("X")))
# """
TypeRaisingRight = Inference("T<",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
    Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X")))),
    lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
    lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
)

# """
# TypeRaisingLeft Combinator.
#
# self combinator applies the 'T>' operator for CCG expressions, which represents
# a type raising operation in Combinatory Categorial Grammar (CCG).
#
# Judgements:
# - Input: Judgement of 'a' with a variable type 'X'.
# - Output: Judgement of 'a' with type 'T\(T/X)'.
#
# Semantics:
# - Raises the type 'X' to 'T' and applies a semantic function 'f' if it exists.
#
# Example:
# >>> tr_left = TypeRaisingLeft.match([Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))])
# >>> print(tr_left)
# Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("T"),
#                                                 CCGTypeComposite(0, CCGTypeVar("T"),
#                                                                     CCGTypeVar("X")))
# """
TypeRaisingLeft = Inference("T>",
    [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
     Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeVar("X")))),
     lambda data: LambdaTermLambda("f", LambdaTermApplication(LambdaTermVar("f"), data[0].sem)) if data[0].sem else None,
     lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
)


class CKYDerivation:
    """
    Represents a derivation in the CKY parsing algorithm.

    self class represents a CKY (Cocke-Kasami-Younger) derivation, which is used
    in parsing algorithms for context-free grammars.

    Args:
    - current (CKYDerivation): The current CKY node for self derivation.
    - past (List[CKYDerivation]): A list of past CKY derivations that were combined.
    - combinator (Combinator): The combinator used to combine past derivations.

    Methods:
    - show(sem=False): Generate a string representation of the derivation.
    - sub_show(sem=False): Generate a sub-string representation for internal use.

    Example:
    >>> cky_node = CKYDerivation(...)
    >>> past_derivations = [CKYDerivation(...), CKYDerivation(...)]
    >>> combinator = Combinator(...)
    >>> derivation = CKYDerivation(cky_node, past_derivations, combinator)
    >>> print(derivation.show())
    """

    def __init__(self, current, past, combinator):
        """
        Initialize a CKYDerivation object.

        Args:
        - current (CKYDerivation): The current CKY node for self derivation.
        - past (List[CKYDerivation]): A list of past CKY derivations that
                                        were combined.
        - combinator (Combinator): The combinator used to combine past derivations.

        Example:
        >>> cky_node = CKYDerivation(...)
        >>> past_derivations = [CKYDerivation(...), CKYDerivation(...)]
        >>> combinator = Combinator(...)
        >>> derivation = CKYDerivation(cky_node, past_derivations, combinator)
        """
        self.current = current
        self.past = past
        self.combinator = combinator

    def __str__(self):
        """
        Returns a string representation of the CKY derivation.

        Returns:
        str: A string representation of the CKY derivation.

        Example:
        >>> print(derivation)
        [ Derivation Tree ]
        """
        return self.show()

    def sub_show(self, sem=False):
        """
        Generate a sub-string representation for internal use.

        Args:
        - sem (bool): Whether to include semantic information in the representation.

        Returns:
        Tuple[str, int]: A tuple containing the string representation and its width.

        Example:
        >>> sub_representation = derivation.sub_show(sem=True)
        >>> string_representation, width = sub_representation
        """
        if not self.past:
            current_show = self.current.type.show()
            current_expr = self.current.expr.show()
            if sem:
                current_sem = self.current.sem.show()
                offset = max(len(current_show), len(current_sem), len(current_expr))
                offspace_e = ((offset-len(current_expr))//2)*" "
                offspace_t = ((offset-len(current_show))//2)*" "
                offspace_s = ((offset-len(current_sem))//2)*" "
                return (offspace_e + current_expr + "\n"
                        + offspace_t + current_show + "\n"
                        + offspace_s + current_sem, offset)

            offset = max(len(current_show), len(current_expr))
            offspace_e = ((offset-len(current_expr))//2)*" "
            offspace_t = ((offset-len(current_show))//2)*" "
            return (offspace_e + current_expr + "\n"
                    + offspace_t + current_show, offset)

        if len(self.past) == 1:
            current_show = self.current.type.show()
            comb = self.combinator.name
            top, size = self.past[0].sub_show(sem)

            if sem:
                current_sem = self.current.sem.show()
                offset = max(len(current_show), len(current_sem), size)
                ntop = top.split("\n")
                res = ""
                offspace_s = ((offset-len(current_sem))//2)*" "
                offspace_t = ((offset-len(current_show))//2)*" "
                offspace_sz = ((offset-size)//2)*" "
                for step in ntop:
                    res += offspace_sz + step + "\n"
                return (res + offset*"=" + comb + "\n"
                        + offspace_t + current_show + "\n"
                        + offspace_s + current_sem, offset)

            offset = max(len(current_show), size)
            ntop = top.split("\n")
            res = ""
            offspace_t = ((offset-len(current_show))//2)*" "
            offspace_sz = ((offset-size)//2)*" "
            for step in ntop:
                res += offspace_sz + step + "\n"
            return (res + offset*"=" + comb + "\n"
                    + offspace_t + current_show, offset)

        if len(self.past) == 2:
            topl, sizel = self.past[0].sub_show(sem)
            topr, sizer = self.past[1].sub_show(sem)
            totsize = sizel+sizer+3
            toplm = topl.split("\n")
            toprm = topr.split("\n")
            current_show = self.current.type.show()

            comb = self.combinator.name
            if sem:
                current_sem = self.current.sem.show()
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

            offspace_s = ((offset-len(current_sem))//2)*" "
            offspace_t = ((offset-len(current_show))//2)*" "
            if sem:
                return (res + offset*"=" + comb + "\n"
                        + offspace_t + current_show + "\n"
                        + offspace_s + current_sem, offset)
            return (res + offset*"=" + comb + "\n"
                    + offspace_t + current_show, offset)
        raise NotImplementedError()

    def show(self, sem=False):
        """
        Generate a string representation of the CKY derivation.

        Args:
        - sem (bool): Whether to include semantic information in the representation.

        Returns:
        str: A string representation of the CKY derivation.

        Example:
        >>> print(derivation.show(sem=True))
        """
        return self.sub_show(sem=sem)[0]


def add_combinations(combinators, left, right, current_chart):
    """
    Add valid combinations of combinators to the current chart.

    Args:
        combinators (list of Inference): List of combinators to be applied.
        left (Judgement): Left-side judgement.
        right (Judgement): Right-side judgement.
        current_chart (set of Judgement): Current chart of judgements.

    Returns:
        set of Judgement: Updated chart with valid combinations.

    Example:
    >>> combinators = [ApplicationLeft, ApplicationRight, CompositionLeft,
                       CompositionRight, TypeRaisingRight, TypeRaisingLeft]
    >>> left = Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"), CCGTypeVar("Y")))
    >>> right = Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
    >>> chart = set()
    >>> result = add_combinations(combinators, left, right, chart)
    >>> print(result)
    {0: {1: {Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")), CCGTypeVar("X")}}}
    """
    for combinator in combinators:
        result = combinator.match([left, right])
        if result:
            current_chart.add(result)
    return current_chart


def compute_chart(combinators, chart, span, start, use_typer=False):
    """
    Compute the chart of valid derivations for a given span of input.

    Args:
        combinators (list of Inference): List of combinators to be applied.
        chart (dict of dict of set): Chart of judgements.
        span (int): Span of the input to consider.
        start (int): Start position for the span.
        use_typer (bool): Flag to enable type-raising.

    Returns:
        set of Judgement: Updated chart with valid derivations.

    Example:
    >>> combinators = [ApplicationLeft, ApplicationRight, CompositionLeft,
                        CompositionRight, TypeRaisingRight, TypeRaisingLeft]
    >>> chart = {0: {1: {Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"),
                                                                        CCGTypeVar("Y"))}},
                 1: {1: {Judgement(CCGExprVar("b"), CCGTypeVar("Y")}}}
    >>> span = 2
    >>> start = 0
    >>> use_typer = False
    >>> result = compute_chart(combinators, chart, span, start, use_typer)
    >>> print(result)
    {0: {1: {Judgement(CCGExprVar("a"), CCGTypeComposite(1, CCGTypeVar("X"),
                                                            CCGTypeVar("Y"))}},
     1: {1: {Judgement(CCGExprVar("b"), CCGTypeVar("Y")}},
         0: {2: {Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
                                                          CCGTypeVar("X")}}}}
    """
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
    """
    Reconstruct CKY derivations from judgements.

    Args:
        parses (list of judgements): List of parse trees.

    Returns:
        list of CKYDerivation: List of reconstructed CKY derivations.

    Example:
    >>> parses = [parse_tree1, parse_tree2]
    >>> result = reconstruct(parses)
    >>> print(result)
    [CKYDerivation(parse1), CKYDerivation(parse2)]
    """
    result = []
    for parse in parses:
        for deriv in parse.derivation:
            if deriv["derivation"]:
                past = reconstruct(deriv["derivation"][2])
                result.append(CKYDerivation(parse, past, deriv["derivation"][0]))
            else:
                result.append(CKYDerivation(parse, None, None))
    return result


def CCGCKYParser(ccg, input_string, use_typer=False):
    """
    Parse a given input string using Combinatory Categorial Grammar (CCG) and CKY parsing.

    Args:
        ccg (CCGGrammar): The CCG grammar for parsing.
        input_string (str): The input string to parse.
        use_typer (bool, optional): Flag to enable type-raising (default is False).

    Returns:
        list of CKYDerivation: List of reconstructed CKY derivations.

    Example:
    >>> ccg = CCGGrammar(...)
    >>> input_string = "John eats apples"
    >>> use_typer = True
    >>> result = CCGCKYParser(ccg, input_string, use_typer)
    >>> print(result)
    [CKYDerivation(parse1), CKYDerivation(parse2), ...]

    Raises:
        TokenError: If a token in the input string is not recognized in the CCG grammar.
    """
    if not input_string or input_string.isspace():
        raise SyntaxError("Empty input")
    tokens = input_string.strip().split()
    num_tokens = len(tokens)
    chart = {}
    combinators = {ApplicationLeft, ApplicationRight, CompositionLeft, CompositionRight}
    # Reconnaisance des symboles terminaux
    for i, token in enumerate(tokens):
        if token not in ccg.rules:
            raise TokenError(token)

        chart[(i, i+1)] = set(ccg.rules[token])

    for span in range(2, num_tokens + 1):
        for start in range(0, num_tokens - span + 1):
            chart[(start, start + span)] = compute_chart(combinators, chart, span, start, use_typer)

    return reconstruct([elem for elem in chart[(0, num_tokens)] if elem.type.show() == ccg.terminal])
