"""
CCGrammar Module

This module provides Python implementations for parsing, processing, and
working with Combinatory Categorial Grammar (CCG) definitions.
It defines several classes and functions for CCG manipulation.

Classes:
- `CCGrammar`: Represents a Combinatory Categorial Grammar (CCG) and provides
                methods for parsing and processing CCG grammar definitions.
- `Judgement`: Represents a judgment in a CCG, including expression, type,
                semantics, and derivation information.
- `Alias`: Represents an alias definition in a CCG, including the key and
            its associated value.
- `Weight`: Represents a combinator weight in a CCG, associated with premises
            and a weight value.
- `ParseError`: An exception raised for errors in the parsing of CCG grammars.
- Several other helper classes related to CCG types, lambda terms, and more.

Functions:
- Various utility functions for parsing and processing CCG grammar elements.

Example:
    >>> grammar_str = "Your CCGrammar Definition Here"
    >>> parsed_statements = CCGrammar.parse(grammar_str)
    >>> grammar = CCGrammar(grammar_str)
    >>> print(grammar.axioms)
    >>> print(grammar.aliases)
    >>> print(grammar.rules)
    >>> print(grammar.weights)
    >>> print(grammar.terminal)
    >>> print(grammar.show())
"""
from functools import reduce
from itertools import product
from RDParser import RDParser as rd
from CCGExprs import CCGExprString
from CCGTypes import (CCGType, CCGTypeVar, CCGTypeAtomic, CCGTypeComposite,
                      CCGTypeAnnotation)
from CCGLambdas import (LambdaTermVar, LambdaTermBinop, LambdaTermPredicate,
                        LambdaTermApplication, LambdaTermLambda,
                        LambdaTermExists)


class ParseError(Exception):
    """Exception raised for errors in the parsing.

    Attributes:
        grammar -- the parsed grammar
        message -- explanation of the error
    """

    def __init__(self, gram, msg="There was a parsing error on the grammar"):
        self.grammar = gram
        self.message = msg
        super().__init__(self.message)


def sel(idx, parse):
    """
    Select and return a specific element from the result of a
    parsing operation.

    Args:
    - idx (int): The index of the element to select from the parsing result.
    - parse: A parsing operation that produces a result.

    Returns:
    Any: The selected element from the parsing result.

    This function takes an index (`idx`) and a parsing operation (`parse`)
    as input.
    It then applies the parsing operation and returns the element at the
    specified index from the result.

    Example:
    >>> result = sel(1, rd.seq("Hello", "World"))("Hello World")
    >>> print(result)
    # Output: 'World'
    """
    return rd.act(parse, lambda x: x[idx])


Identifier = rd.rgx("[a-zA-Zéèêà_][a-zA-Zéèêà_0-9]*")
Integer = rd.rgx("[0-9]+")
Float = rd.act(rd.rgx("[0-9]+(\\.[0-9]+)?"), float)
Spaces = rd.rgx("( |\t)+")
DQuoString = rd.act(rd.rgx("\"([^\"]+)\""), lambda x: x[1:][:-1])

CCGTypeParser = rd.grow("type", lambda type: rd.alt(
    rd.act(rd.seq(type, rd.str("["), Identifier, rd.str("]")), lambda x: CCGTypeAnnotation(x[0], x[2])),
    rd.act(rd.seq(type, rd.alt(rd.str("\\"), rd.str("/")), type), lambda x: CCGTypeComposite(x[1] == '/', x[0], x[2])),
    rd.act(sel(1, rd.seq(rd.str("$"), rd.raw(Identifier))), CCGTypeVar),
    rd.act(rd.seq(rd.str("("), type, rd.str(")")), lambda x: x[1]),
    rd.act(Identifier, CCGTypeAtomic),
))

LambdaTermParser = rd.grow('expr', lambda expr: rd.alt(
    rd.act(rd.seq(expr, rd.str(" "), expr), lambda x: LambdaTermApplication(x[0], x[2])),
    rd.act(rd.seq(expr, rd.rgx("\\+|\\&|\\|"), expr), lambda x: LambdaTermBinop(x[1], x[0], x[2])),
    rd.act(rd.seq(Identifier, rd.raw(rd.str("(")), rd.lst(sel(0, rd.seq(expr, rd.mbe(rd.str(","))))), rd.str(")")), lambda x: LambdaTermPredicate(LambdaTermVar(x[0]), x[2])),
    rd.act(rd.seq(rd.str("\\"), rd.act(rd.lst1(Identifier), lambda x: [x.reverse(), x][1]), rd.str("."), expr), lambda x: reduce(LambdaTermLambda.build, x[1], x[3])),
    rd.act(rd.seq(rd.str("exists"), rd.rgx("\\s+"), rd.lst1(Identifier), rd.str("."), expr), lambda x: reduce(LambdaTermExists.build, x[2], x[4])),
    rd.act(rd.seq(rd.str("("), expr, rd.str(")")), lambda x: x[1]),
    rd.act(Identifier, LambdaTermVar)
))


class Judgement:
    """
    Represents a judgment in a Combinatory Categorial Grammar (CCG).

    This class provides a representation for a judgment, including the
    expression, type, semantics, and derivation information.
    It offers methods for displaying the judgment, expanding it with new
    values, matching it with another judgment, replacing values,
    and deriving new judgments.

    Attributes:
    - expr (CCGExprString): The expression of the judgment.
    - type (CCGTypeParser): The type of the judgment.
    - cpt (int): A counter for the judgment.
    - sem (Optional[CCGTypeParser]): The semantics associated with the
                                     judgment.
    - derivation (list): Information about the derivation of the judgment.

    Methods:
    - show(printsem=False): Generate a string representation of the judgment.
    - expand(name, type): Expand the judgment with a new name and type.
    - match(data, sigma): Match the judgment with another judgment.
    - replace(sigma): Replace values in the judgment based on a substitution.
    - deriving(combinator, sigma, judmts, sem=None): Derive new judgments
            based on combinator, substitution, and input judgments.

    Example:
    >>> expr = CCGExprString("your_expression")
    >>> type = CCGTypeParser("your_type")
    >>> judgment = Judgement(expr, type, sem=CCGTypeParser("semantics"))
    >>> print(judgment.show())
    >>> new_judgment = judgment.expand("new_name", CCGTypeParser("new_type"))
    >>> result = judgment.match(new_judgment, sigma)
    >>> replaced_judgment = judgment.replace(sigma)
    >>> new_judgments = judgment.deriving("combinator", sigma,
                                          [judgment1, judgment2],
                                           sem=CCGTypeParser("new_semantics"))
    """
    def __init__(self, expr, type_judg, sem=None, derivation=None, weight=1):
        """
        Initialize a Judgement object with the provided expression, type,
        semantics, and derivation information.

        Args:
        - expr (CCGExprString): The expression of the judgment.
        - type (CCGTypeParser): The type of the judgment.
        - sem (Optional[CCGTypeParser]): The semantics associated with the
                                        judgment (default is None).
        - derivation (Optional[list]): Information about the derivation of the
        judgment (default is a list with weight and empty derivation).
        - weight (int): The weight associated with the judgment (default is 1).

        Example:
        >>> expr = CCGExprString("your_expression")
        >>> type = CCGTypeParser("your_type")
        >>> judgment = Judgement(expr, type, sem=CCGTypeParser("semantics"))
        """
        self.expr = expr
        self.type = type_judg
        self.cpt = 0
        self.sem = sem
        self.derivation = derivation if derivation else [{"weight": weight,
                                                          "derivation": []}]

    def show(self, printsem=False):
        """
        Generate a string representation of the judgment.

        Args:
        - printsem (bool): Whether to include semantics in the representation
                            (default is False).

        Returns:
        str: A string representation of the judgment.

        Example:
        >>> print(judgment.show())
        """
        sem = (" { %s }" % self.sem.show()) if printsem and self.sem else ""
        return f"{self.expr.show()}:{self.type.show()}{sem}"

    def expand(self, name, type_judg):
        """
        Expand the judgment with a new name and type.

        Args:
        - name (str): The new name for the expanded judgment.
        - type_judg (CCGTypeParser): The new type for the expanded judgment.

        Returns:
        Judgement: A new Judgement object with the expanded name and type.

        Example:
        >>> new_judgment = judgment.expand("new_name",
                                           CCGTypeParser("new_type"))
        """
        ex = self.type.expand(name, type_judg)
        return Judgement(self.expr, ex, sem=self.sem, derivation=self.derivation)

    def match(self, data, sigma):
        """
        Match the judgment with another judgment using a substitution.

        Args:
        - data (Judgement): The other judgment to match against.
        - sigma (Substitution): The substitution to apply during matching.

        Returns:
        Union[None, bool]: True if the judgments match, None if no
                           match is found.

        Example:
        >>> result = judgment.match(new_judgment, sigma)
        """
        if not self.expr.match(data.expr, sigma):
            return None
        # ~ if not self.type.match(data.type, sigma):
            # ~ return None
        if not CCGType.unify(self.type, data.type, sigma):
            return None
        return True

    def replace(self, sigma):
        """
        Replace values in the judgment based on a substitution.

        Args:
        - sigma (Substitution): The substitution to apply during replacement.

        Returns:
        Judgement: A new Judgement object with values replaced based on the
        substitution.

        Example:
        >>> replaced_judgment = judgment.replace(sigma)
        """
        exp = self.expr.replace(sigma)
        typ = self.type.replace(sigma)
        der = self.derivation
        return Judgement(exp, typ, sem=self.sem, derivation=der)

    def deriving(self, combinator, sigma, judmts, sem=None):
        """
        Derive new judgments based on combinator, substitution, and input
        judgments.

        Args:
        - combinator (str): The combinator used for derivation.
        - sigma (Substitution): The substitution to apply during derivation.
        - judmts (list): List of input judgments to derive new judgments.
        - sem (Optional[CCGTypeParser]): The semantics associated with the
                                        derived judgments (default is None).

        Returns:
        Judgement: The current Judgement object with updated derivation
                    and semantics.

        Example:
        >>> new_judgments = judgment.deriving("combinator", sigma,
                                            [judgment1, judgment2],
                                            sem=CCGTypeParser("new_semantics"))
        """
        self.derivation = []
        derivations_list = [judgment.derivation for judgment in judmts]
        for derivations in product(*derivations_list):
            tt_weight = max(derv["weight"] for derv in derivations)
            pst = [combinator, sigma, judmts]
            der = {"weight": tt_weight, "derivation": pst}
            self.derivation.append(der)
        self.sem = sem
        return self


class Alias:
    """
    Represents an alias definition in a Combinatory Categorial Grammar (CCG).

    This class provides a representation for an alias, including its key and
    value.
    It also offers methods for displaying the alias and expanding it with
    new values.

    Attributes:
    - key (str): The alias key.
    - value (CCGTypeParser): The value associated with the alias.

    Methods:
    - show(): Generate a string representation of the alias.
    - expand(key, value): Expand the alias with new key and value.

    Example:
    >>> alias = Alias("AliasName", CCGTypeParser("AliasValue"))
    >>> print(alias.show())
    >>> new_alias = alias.expand("NewAliasName",
                                 CCGTypeParser("NewAliasValue"))
    """

    def __init__(self, key, value):
        """
        Initialize an Alias object with the provided key and value.

        Args:
        - key (str): The alias key.
        - value (CCGTypeParser): The value associated with the alias.

        Example:
        >>> alias = Alias("AliasName", CCGTypeParser("AliasValue"))
        """
        self.key = key
        self.value = value

    def show(self):
        """
        Generate a string representation of the alias.

        Returns:
        str: A string representation of the alias in the format
             "key = value.show()".

        Example:
        >>> alias = Alias("AliasName", CCGTypeParser("AliasValue"))
        >>> print(alias.show())
        """
        return f"{self.key} = {self.value.show()}"

    def expand(self, key, value):
        """
        Expand the alias with a new key and value.

        Args:
        - key (str): The new key for the expanded alias.
        - value (CCGTypeParser): The new value for the expanded alias.

        Returns:
        Alias: A new Alias object with the expanded key and value.

        Example:
        >>> alias = Alias("AliasName", CCGTypeParser("AliasValue"))
        >>> new_alias = alias.expand("NewAliasName",
                                     CCGTypeParser("NewAliasValue"))
        """
        return Alias(self.key, self.value.expand(key, value))


class Weight:
    """
    Represents a combinator weight in a Combinatory Categorial Grammar (CCG).

    This class provides a representation for a combinator weight, including
    its combinator name, premises, and the weight value. It also offers a
    method for matching weights in the grammar.

    Attributes:
    - combinator_name (str): The name of the combinator associated
                            with the weight.
    - premises (list): A list of premises for the weight.
    - weight (float): The weight value.

    Methods:
    - match(combinator, sigma): Match this weight against a combinator
                                and sigma.

    Example:
    >>> weight = Weight("combinator_name", ["Premise1", "Premise2"], 0.5)
    >>> result = weight.match(combinator, sigma)
    """
    def __init__(self, combinator_name, premices, weight):
        """
        Initialize a Weight object with the provided combinator name, premises,
        and weight.

        Args:
        - combinator_name (str): The name of the combinator associated with
                                the weight.
        - premices (list): A list of premises for the weight.
        - weight (float): The weight value.

        Example:
        >>> weight = Weight("combinator_name", ["Premise1", "Premise2"], 0.5)
        """
        self.combinator_name = combinator_name
        self.premices = premices
        self.weight = weight

    def match(self, combinator, sigma):
        """
        Match this weight against a combinator and sigma.

        Args:
        - combinator (str): The combinator to match.
        - sigma (list): The sigma list.

        Returns:
        - bool: True if the weight matches the combinator and sigma;
                False otherwise.

        Example:
        >>> weight = Weight("combinator_name", ["Premise1", "Premise2"], 0.5)
        >>> result = weight.match("SomeCombinator", ["Premise1", "Premise2"])
        >>> print(result)
        """
        # ~ if len(self.premices) == len(premices):
        #     ~ for (l, r) in zip(self.premices, premices):
        #         ~ if not (l == r):


WeightParser = rd.act(
    rd.seq(
        rd.str("Weight"),
        rd.str("("),
        DQuoString,
        rd.lst1(rd.act(rd.seq(rd.str(","), CCGTypeParser), lambda x: x[1])),
        rd.str(")"),
        rd.str("="),
        Float
    ),
    lambda x: Weight(x[2], x[3], x[6])
)


class CCGrammar:
    """
    Represents a Combinatory Categorial Grammar (CCG) and provides methods for
    parsing and processing CCG grammar definitions.

    This class allows you to create a CCGrammar object from a string
    representation of the grammar, parse the grammar, and perform operations
    such as expanding aliases, displaying the grammar, and more.

    Attributes:
    - axioms (dict): A dictionary of axioms and their type expressions.
    - aliases (dict): A dictionary of aliases and their definitions.
    - rules (dict): A dictionary of rules for type judgments.
    - weights (dict): A dictionary of combinator weights.
    - terminal (str): The terminal axiom.

    Methods:
    - parse(grammar_str): Parse a CCGrammar definition string and return a
                          list of statements.
    - __init__(str_gram): Initialize a CCGrammar object from a string
                            representation of the grammar.
    - process_axioms(axioms): Process and store axioms from the grammar
                                definition.
    - process_alias(alias): Process and store an alias definition from
                            the grammar.
    - process_judgment(judgment): Process and store a judgment from
                                    the grammar.
    - process_weight(weight): Process and store a weight definition from
                                the grammar.
    - expand_aliases(): Expand aliases in the grammar.
    - show(): Generate a string representation of the CCGrammar object.
    """
    newLines = rd.lst1(rd.str("\n"))
    axiom = sel(0, rd.seq(Identifier, rd.mbe(rd.str(","))))
    axioms = rd.act(rd.seq(rd.str(":-"), rd.lst1(axiom)), lambda x: {"axioms": x[1]})
    alias = rd.act(rd.seq(Identifier, rd.str("::"), CCGTypeParser), lambda x: {"alias": Alias(x[0], x[2])})
    weight = rd.alt(rd.act(rd.seq(rd.str("("), Integer, rd.str(")")), lambda x: int(x[1])), rd.val(0))
    lmbda = sel(1, rd.seq(rd.str("{"), LambdaTermParser, rd.str("}")))
    judgm = rd.act(
        rd.seq(rd.rgx("[^\\s]+"), rd.str("=>"), weight, CCGTypeParser, rd.mbe(lmbda)),
        lambda x: {"judgm": Judgement(CCGExprString(x[0]), x[3], weight=x[2], sem=x[4])}
    )
    weightRule = rd.act(WeightParser, lambda x: {"weight": x})
    comment = rd.act(rd.seq(rd.str("#"), rd.rgx(".*")), lambda x: None)
    grammar = sel(0, rd.seq(rd.lst(sel(1, rd.seq(newLines, rd.alt(comment, axioms, alias, judgm, weightRule)))), newLines, rd.end()))

    @classmethod
    def parse(cls, grammar_str):
        """
        Parse a CCGrammar definition string and return a list of statements.

        Args:
        - grammar_str (str): A string containing the CCGrammar definition.

        Returns:
        - list: A list of parsed statements from the grammar definition.

        Raises:
        - ParseError: If the parsing of the grammar string fails.

        This class method parses a CCGrammar definition string and returns a
        list of statements, including axioms, aliases, judgments, and weights.
        If the parsing fails, it raises a `ParseError` exception.

        Example usage:
        >>> grammar_str = "Your CCGrammar Definition Here"
        >>> parsed_statements = CCGrammar.parse(grammar_str)
        >>> for stmt in parsed_statements:
        >>>     print(stmt)
        """
        res = cls.grammar(grammar_str, {}, Spaces)
        if res:
            return res[0]
        raise ParseError(grammar_str)

    def __init__(self, str_gram):
        """
        Initialize a CCGrammar object from a string representation of the
        grammar.

        Args:
        - str_gram (str): A string containing the CCGrammar definition.

        This method parses the provided string representation of the grammar
        and initializes the CCGrammar object with axioms, aliases, rules,
        and weights.

        Example usage:
        >>> grammar = CCGrammar("Your CCGrammar Definition Here")
        >>> print(grammar.axioms)
        >>> print(grammar.aliases)
        >>> print(grammar.rules)
        >>> print(grammar.weights)
        >>> print(grammar.terminal)
        """
        self.axioms = {}
        self.aliases = {}
        self.rules = {}
        self.weights = {}
        self.terminal = None

        for stmt in self.parse(str_gram):
            if stmt is None:
                pass
            elif "axioms" in stmt:
                self.process_axioms(stmt["axioms"])
            elif "alias" in stmt:
                self.process_alias(stmt["alias"])
            elif "judgm" in stmt:
                self.process_judgment(stmt["judgm"])
            elif "weight" in stmt:
                self.process_weight(stmt["weight"])

        self.expand_aliases()

    def process_axioms(self, axioms):
        """
        Process and store axioms from the grammar definition.

        Args:
        - axioms (list): A list of axiom strings.

        This method processes and stores the axioms defined in the grammar.

        Example usage:
        >>> axioms = ["Nom[Masc]", "Nom[Fem]"]
        >>> process_axioms(axioms)
        """
        for ax in axioms:
            if self.terminal:
                self.axioms[ax] = ax
            else:
                self.terminal = ax

    def process_alias(self, alias):
        """
        Process and store an alias definition from the grammar.

        Args:
        - alias (Alias): An Alias object representing an alias definition.

        This method processes and stores alias definitions from the grammar.

        Example usage:
        >>> alias = Alias("AliasName", "AliasValue")
        >>> process_alias(alias)
        """
        self.aliases[alias.key] = alias

    def process_judgment(self, judgment):
        """
        Process and store a judgment from the grammar.

        Args:
        - judgment (Judgment): A Judgment object representing a judgment
                                definition.

        This method processes and stores judgment definitions from the grammar.

        Example usage:
        >>> judgment = Judgment(expr, rule)
        >>> process_judgment(judgment)
        """
        expr_str = judgment.expr.str
        if expr_str not in self.rules:
            self.rules[expr_str] = []
        self.rules[expr_str].append(judgment)

    def process_weight(self, weight):
        """
        Process and store a weight definition from the grammar.

        Args:
        - weight (Weight): A Weight object representing a weight definition.

        This method processes and stores weight definitions from the grammar.

        Example usage:
        >>> weight = Weight("combinator_name", weight_value)
        >>> process_weight(weight)
        """
        combinator_name = weight.combinator_name
        if combinator_name not in self.weights:
            self.weights[combinator_name] = []
        self.weights[combinator_name].append(weight)

    def expand_aliases(self):
        """
        Expand aliases in the grammar.

        This method expands aliases in the grammar rules and definitions.

        Example usage:
        >>> expand_aliases()
        """
        for (_, alv) in self.aliases.items():
            for (elk, elv) in self.aliases.items():
                self.aliases[elk] = elv.expand(alv.key, alv.value)
            for (rulk, rulvs) in self.rules.items():
                self.rules[rulk] = [r.expand(alv.key, alv.value) for r in rulvs]

    def show(self):
        """
        Generate a string representation of the CCGrammar object.

        This method returns a string representation of the CCGrammar object,
        including its axioms, aliases, and rules. The axioms are listed with
         their respective type expressions, aliases are shown, and rules are
         displayed in a readable format.

        Returns:
        str: A string representation of the CCGrammar object.

        Example:
        >>> grammar = CCGrammar("Your CCGrammar Definition Here")
        >>> print(grammar.show())
        :- axioms, listed, here
        AliasA = TypeExpressionA
        AliasB = TypeExpressionB
        "word1": typeofword1
        "word2": typeofword2
        """
        srule = [f"{r.show()}" for rl in self.rules.values() for r in rl]
        rules = "\n".join(srule)
        axioms = ":- " + ", ".join(self.axioms.keys())
        aliases = "\n".join([v.show() for v in self.aliases.values()])
        return "\n".join([axioms, aliases, rules])
