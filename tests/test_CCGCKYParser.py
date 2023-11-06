import unittest
from CCGCKYParser import (CCGCKYParser, TokenError, Inference,
                          CKYDerivation, add_combinations,
                          Judgement, CCGExprVar, CCGTypeComposite, CCGExprConcat,
                          CCGTypeVar, ApplicationLeft, ApplicationRight,
                          CompositionLeft, CompositionRight,
                          TypeRaisingLeft, TypeRaisingRight)
from CCGrammar import CCGrammar
from CCGExprs import CCGExprString
from CCGTypes import CCGTypeAtomic, CCGTypeAtomicVar
from CCGLambdas import LambdaTermLambda, LambdaTermApplication, LambdaTermVar
from nltk.tree import Tree

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
        cls.d1 = Judgement(CCGExprString('fruit'), CCGTypeAtomic("NP"))
        cls.d2 = Judgement(CCGExprString('apple'), CCGTypeComposite(0, CCGTypeAtomic("S"), CCGTypeAtomic("NP")))
        cls.data = [cls.d1, cls.d2]


        cls.combinator = Inference("$R", [cls.hyp1, cls.hyp2], cls.concl, lambda data: LambdaTermVar("x"))
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

        tr = Inference("T<",
            [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
            Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X")))),
            lambda data: LambdaTermVar("x"),
            lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
        )
        c2 = tr.match([self.current])
        derivation2 = CKYDerivation(c2, [derivation], tr)

        cr = Inference("B<",
            [
                Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y"))),
                Judgement(CCGExprVar("b"), CCGTypeComposite(0, CCGTypeVar("Y"), CCGTypeVar("Z"))),
            ],
            Judgement(
                CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
                CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Z"))
            ),
            lambda data: LambdaTermLambda("x", LambdaTermApplication(LambdaTermVar("y"), LambdaTermApplication(LambdaTermVar("y"), LambdaTermVar("x"))))
        )

        cr_data = Judgement(CCGExprString("tomato"), CCGTypeComposite(0, CCGTypeComposite(1, CCGTypeAtomic("NP"), CCGTypeAtomicVar("S")), CCGTypeAtomic("N")))

        c3 = cr.match([c2, cr_data])
        derivation3 = CKYDerivation(c3, [derivation, derivation2], cr)
        derivation3b = CKYDerivation(c3, [derivation2, derivation], cr)
        derivation_not = CKYDerivation(c3, [derivation2, derivation, derivation2], cr)

        sub_representation1, width1 = derivation.sub_show(sem=False)
        sub_representation1s, width1s = derivation.sub_show(sem=True)
        sub_representation2, width2 = derivation2.sub_show(sem=False)
        sub_representation2s, width2s = derivation2.sub_show(sem=True)
        sub_representation3, width3 = derivation3.sub_show(sem=False)
        sub_representation3s, width3s = derivation3.sub_show(sem=True)
        sub_representation3b, width3b = derivation3b.sub_show(sem=False)
        sub_representation3bs, width3bs = derivation3b.sub_show(sem=True)
        self.assertIsInstance(sub_representation1, str)
        self.assertIsInstance(width1, int)
        self.assertIsInstance(sub_representation1s, str)
        self.assertIsInstance(width1s, int)
        self.assertIsInstance(sub_representation2, str)
        self.assertIsInstance(width2, int)
        self.assertIsInstance(sub_representation2s, str)
        self.assertIsInstance(width2s, int)
        self.assertIsInstance(sub_representation3, str)
        self.assertIsInstance(width3, int)
        self.assertIsInstance(sub_representation3s, str)
        self.assertIsInstance(width3s, int)
        self.assertIsInstance(sub_representation3b, str)
        self.assertIsInstance(width3b, int)
        self.assertIsInstance(sub_representation3bs, str)
        self.assertIsInstance(width3bs, int)
        self.assertGreater(width3, width2 + width1)
        self.assertGreater(width2, width1)
        self.assertGreater(width3s, width2s + width1s)
        self.assertGreater(width2s, width1s)
        self.assertGreater(width3bs, width2s + width1s)
        self.assertGreater(width3b, width2 + width1)

        with self.assertRaises(NotImplementedError):
            derivation_not.sub_show()

    def test_show(self):
        past = None
        derivation = CKYDerivation(self.current, past, self.combinator)
        string_representation = derivation.show()

        self.assertIsInstance(string_representation, str)

    def test_to_nltk_tree(self):

        derivation = CKYDerivation(self.current, None, self.combinator)

        tr = Inference("T<",
            [Judgement(CCGExprVar("a"), CCGTypeAtomicVar("X"))],
            Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("T"), CCGTypeComposite(1, CCGTypeVar("T"), CCGTypeVar("X")))),
            lambda data: LambdaTermVar("x"),
            lambda x: (x[0], x[1].replace({"T": CCGTypeVar(x[1].type.fresh("T"))}))
        )
        c2 = tr.match([self.current])
        derivation2 = CKYDerivation(c2, [derivation], tr)

        cr = Inference("B<",
            [
                Judgement(CCGExprVar("a"), CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Y"))),
                Judgement(CCGExprVar("b"), CCGTypeComposite(0, CCGTypeVar("Y"), CCGTypeVar("Z"))),
            ],
            Judgement(
                CCGExprConcat(CCGExprVar("a"), CCGExprVar("b")),
                CCGTypeComposite(0, CCGTypeVar("X"), CCGTypeVar("Z"))
            ),
            lambda data: LambdaTermLambda("x", LambdaTermApplication(LambdaTermVar("y"), LambdaTermApplication(LambdaTermVar("y"), LambdaTermVar("x"))))
        )

        cr_data = Judgement(CCGExprString("tomato"), CCGTypeComposite(0, CCGTypeComposite(1, CCGTypeAtomic("NP"), CCGTypeAtomicVar("S")), CCGTypeAtomic("N")))

        c3 = cr.match([c2, cr_data])
        derivation3 = CKYDerivation(c3, [derivation, derivation2], cr)
        derivation3b = CKYDerivation(c3, [derivation2, derivation], cr)
        tree = derivation.to_nltk_tree()
        tree2 = derivation2.to_nltk_tree()
        tree3 = derivation3.to_nltk_tree()
        tree3b = derivation3b.to_nltk_tree()
        self.assertIsInstance(tree, str)
        self.assertEqual(tree, self.current.show())
        self.assertIsInstance(tree2, Tree)
        self.assertIsInstance(tree3, Tree)
        self.assertIsInstance(tree3b, Tree)
        self.assertEqual(len(tree2), 1)
        self.assertEqual(len(tree3), 2)
        self.assertEqual(len(tree3b), 2)
        self.assertEqual(tree3b.height(), 3)
        self.assertEqual(tree3.height(), 3)
        self.assertEqual(tree2.height(), 2)
        self.assertEqual(tree3b.label(), '"apple fruit tomato":(NP \\ N)')
        self.assertEqual(tree3.label(), '"apple fruit tomato":(NP \\ N)')
        self.assertEqual(tree2.label(), '"apple fruit":($T_27 \\ ($T_27 / $X))')
