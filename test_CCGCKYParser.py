import unittest
from CCGCKYParser import (CCGCKYParser, TokenError,
                          CKYDerivation, add_combinations,
                          Judgement, CCGExprVar, CCGTypeComposite, CCGExprConcat,
                          CCGTypeVar, ApplicationLeft, ApplicationRight,
                          CompositionLeft, CompositionRight,
                          TypeRaisingLeft, TypeRaisingRight, CCGTypeAtomicVar)
from CCGrammar import CCGrammar

class TestCCGParser(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.ccg = CCGrammar(''':- S, N, NP
                        Adv :: S/NP
                        apples => NP
                        𝒶𝓅𝓅𝓁𝑒𝓈 => NP
                        eats => (S/NP)\\NP
                        eat => (S/NP)\\NP
                        eat => (S\\NP)/NP
                        and => (NP/NP)\\NP
                        John => NP
                        Mary => NP''')

    def test_valid_input(self):
        input_string = '''John eats apples'''
        use_typer = False
        result = CCGCKYParser(self.ccg, input_string, use_typer)

        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(derivation, CKYDerivation) for derivation in result))

    def test_invalid_token(self):
        ccg = CCGrammar(''':- S, N, NP
                        Adv :: S/NP
                        apples => NP
                        eats => (S/NP)\\NP
                        John => NP''')
        input_string = "John eats apples !@#$"  # Intentionally includes invalid tokens
        use_typer = True

        with self.assertRaises(TokenError):
            CCGCKYParser(self.ccg, input_string, use_typer)

    def test_no_input(self):
        ccg = CCGrammar(''':- S, N, NP
                        Adv :: S/NP
                        apples => NP
                        eats => (S/NP)\\NP
                        John => NP''')
        input_string = ""
        use_typer = True

        with self.assertRaises(SyntaxError):
            CCGCKYParser(self.ccg, input_string, use_typer)

    def test_non_grammatical_input(self):
        input_string = "eats John apples"
        use_typer = True
        result = CCGCKYParser(self.ccg, input_string, use_typer)

        self.assertIsInstance(result, list)
        self.assertFalse(result)  # Ensure non-grammatical input produces no derivations

    def test_ambiguous_input(self):
        input_string = "John and Mary eat apples"
        use_typer = False
        result = CCGCKYParser(self.ccg, input_string, use_typer)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)  # Ensure that the input is ambiguous

    def test_empty_string(self):
        input_string = "  "  # Input with only spaces
        use_typer = True
        with self.assertRaises(SyntaxError):
            CCGCKYParser(self.ccg, input_string, use_typer)

    def test_unicode_characters(self):
        input_string = "John eats 𝒶𝓅𝓅𝓁𝑒𝓈"  # Input with Unicode characters
        use_typer = True
        result = CCGCKYParser(self.ccg, input_string, use_typer)
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)  # Ensure at least one valid derivation

    # def test_add_combinations(self):
    #     combinators = [ApplicationRight, CompositionLeft]
    #
    #     left = Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("S"), CCGTypeVar("Y")))
    #     right = Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
    #     print(CompositionLeft.match([left, right]).type.show())
    #
    #     chart = set()
    #
    #     result = add_combinations(combinators, left, right, chart)
    #     print(result.pop().type.show())
    #
    #     self.assertGreater(len(chart), 0)


if __name__ == '__main__':
    unittest.main()
