import unittest
from CCGCKYParser import (CCGCKYParser, TokenError, Inference,
                          CKYDerivation, add_combinations,
                          Judgement, CCGExprVar, CCGTypeComposite, CCGExprConcat,
                          CCGTypeVar, ApplicationLeft, ApplicationRight,
                          CompositionLeft, CompositionRight,
                          TypeRaisingLeft, TypeRaisingRight)
from CCGrammar import CCGrammar
from CCGExprs import CCGExprString
from CCGTypes import CCGTypeAtomic

class TestUtils(unittest.TestCase):

    def test_add_combinations(self):
        combinators = [ApplicationRight, CompositionLeft, ApplicationLeft, CompositionRight, TypeRaisingLeft, TypeRaisingLeft]
        chart = set()
        left = Judgement(CCGExprVar('"eats"'), CCGTypeComposite(1, CCGTypeComposite(0, CCGTypeAtomic("S"), CCGTypeAtomic("NP")), CCGTypeAtomic("NP")))
        right = Judgement(CCGExprVar('"John"'), CCGTypeAtomic("NP"))
        chart = add_combinations(combinators, left, right, chart)
        self.assertEqual(len(chart), 1)
        self.assertEqual(chart.pop().show(), '"eats John":(S \\ NP)')

class TestInference(unittest.TestCase):

    def test_inference_init(self):
        hyp1 = CCGExprVar("X")
        hyp2 = CCGExprString("apple")
        concl = CCGExprVar("Y")
        inference = Inference("$R", [hyp1, hyp2], concl)

        self.assertEqual(inference.name, "$R")
        self.assertEqual(inference.hyps, [hyp1, hyp2])
        self.assertEqual(inference.concl, concl)
        self.assertIsNone(inference.sem)
        self.assertIsNotNone(inference.helper)  # The default helper function should not be None

    def test_inference_str(self):
        hyp1 = CCGExprVar("X")
        hyp2 = CCGExprString("apple")
        concl = CCGExprVar("Y")
        inference = Inference("$R", [hyp1, hyp2], concl)
        expected_str = 'X, "apple"\n----------$R\n    Y      '

        self.assertEqual(str(inference), expected_str)

    def test_inference_show(self):
        hyp1 = CCGExprVar("X")
        hyp2 = CCGExprString("apple")
        concl = CCGExprVar("Y")
        inference = Inference("$R", [hyp1, hyp2], concl)
        expected_show = 'X, "apple"\n----------$R\n    Y      '

        self.assertEqual(inference.show(), expected_show)

    def test_inference_match_with_valid_data(self):
        # Create and test with Judgement objects (hypotheses and conclusion)
        hyp1 = Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
        hyp2 = Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"),
                                                              CCGTypeVar("Y")))
        concl = Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")), CCGTypeVar("C"))
        inference = Inference("$R", [hyp1, hyp2], concl, lambda data: data[1].sem.apply(data[0].sem) if data[0].sem and data[1].sem else None)
        data = [Judgement(CCGExprString('fruit'), CCGTypeAtomic("NP")), Judgement(CCGExprString('apple'), CCGTypeComposite(0, CCGTypeAtomic("S"),
                                                                                                                            CCGTypeAtomic("NP")))]
        result = inference.match(data)
        self.assertIsInstance(result, Judgement)
        self.assertEqual(result.expr.show(), '"apple fruit"')
        self.assertEqual(result.type.show(), '$C')

    def test_inference_match_with_invalid_data(self):
        hyp1 = CCGExprVar("X")
        hyp2 = CCGExprString("apple")
        concl = CCGExprVar("Y")
        inference = Inference("$R", [hyp1, hyp2], concl)
        data = [CCGExprVar("X"), CCGExprString("pear")]
        result = inference.match(data)

        self.assertIsNone(result)

    def test_inference_replace(self):
        hyp1 = CCGExprVar("X")
        hyp2 = CCGExprString("apple")
        concl = CCGExprVar("Y")
        inference = Inference("$R", [hyp1, hyp2], concl)
        substitution = {"X": CCGExprString("fruit"), "Y": CCGExprString("food")}
        new_inference = inference.replace(substitution)

        self.assertIsInstance(new_inference, Inference)
        self.assertEqual(new_inference.name, "$R")
        self.assertEqual([h.show() for h in new_inference.hyps], [CCGExprString("fruit").show(), hyp2.show()])
        self.assertEqual(new_inference.concl.show(), CCGExprString("food").show())
        self.assertIsNone(new_inference.sem)
        self.assertIsNotNone(new_inference.helper)  # The default helper function should not be None


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
                        and => (S/S)\\S
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

    def test_grammar_with_type_raising(self):
        input_string = "John eats apples"
        use_typer = True
        result = CCGCKYParser(self.ccg, input_string, use_typer)

        self.assertIsInstance(result, list)
        self.assertTrue(all(isinstance(derivation, CKYDerivation) for derivation in result))

    def test_long_input(self):
        input_string = "John eats apples and Mary eats apples"
        use_typer = False
        result = CCGCKYParser(self.ccg, input_string, use_typer)

        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 1)  # Ensure that the input is ambiguous


class TestCKYDerivation(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.hyp1 = Judgement(CCGExprVar("b"), CCGTypeVar("Y"))
        cls.hyp2 = Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"),
                                                              CCGTypeVar("Y")))
        cls.concl = Judgement(CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")), CCGTypeVar("C"))
        cls.data = [Judgement(CCGExprString('fruit'), CCGTypeAtomic("NP")), Judgement(CCGExprString('apple'), CCGTypeComposite(0, CCGTypeAtomic("S"),
                                                                                                                            CCGTypeAtomic("NP")))]


        cls.combinator = Inference("$R", [cls.hyp1, cls.hyp2], cls.concl, lambda data: data[1].sem.apply(data[0].sem) if data[0].sem and data[1].sem else None)
        cls.current = cls.combinator.match(cls.data)

    def test_init(self):
        current = self.current
        past = None
        derivation = CKYDerivation(current, past, self.combinator)

        self.assertEqual(derivation.current, current)
        self.assertEqual(derivation.past, past)
        self.assertEqual(derivation.combinator, self.combinator)

    def test_str(self):
        current = self.current
        past = None
        derivation = CKYDerivation(current, past, self.combinator)
        string_representation = str(derivation)

        self.assertEqual(string_representation, '"apple fruit"\n     $C')

    def test_sub_show(self):
        derivation = CKYDerivation(self.current, None, self.combinator)
        sub_representation, width = derivation.sub_show()

        self.assertIsInstance(sub_representation, str)
        self.assertIsInstance(width, int)

    def test_show(self):
        past = None
        derivation = CKYDerivation(self.current, past, self.combinator)
        string_representation = derivation.show()

        self.assertIsInstance(string_representation, str)

if __name__ == '__main__':
    unittest.main()
