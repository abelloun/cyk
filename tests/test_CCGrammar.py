import unittest
from CCGrammar import CCGrammar, Alias, Judgement, Weight, CCGExprString, CCGTypeParser, ParseError
from CCGTypes import CCGTypeVar

class TestCCGrammar(unittest.TestCase):

    def test_parse_error(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + 'cat ==> N'
        err = ParseError(grammar_str)
        self.assertEqual(grammar_str, err.grammar)
        self.assertIsInstance(err.message, str)

    def test_parse(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + 'cat => N'
        parsed_statements = CCGrammar.parse(grammar_str)

        self.assertTrue(isinstance(parsed_statements, list))
        self.assertGreater(len(parsed_statements), 0)

    def test_parse_fail(self):
        grammar_str = ":- S, N => NP" + "\n" + "Adv :: S/NP" + "\n" + 'cat => N'
        with self.assertRaises(ParseError):
            CCGrammar.parse(grammar_str)

    def test_init_empty(self):
        grammar = CCGrammar("#Only Comments")
        self.assertIsInstance(grammar.axioms, dict)
        self.assertIsInstance(grammar.aliases, dict)
        self.assertIsInstance(grammar.rules, dict)
        self.assertIsInstance(grammar.weights, dict)
        self.assertIsNone(grammar.terminal)
        self.assertEqual({}, grammar.axioms)
        self.assertEqual({}, grammar.aliases)
        self.assertEqual({}, grammar.rules)

    def test_init(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + 'cat => N'
        grammar = CCGrammar(grammar_str)

        self.assertIsInstance(grammar.axioms, dict)
        self.assertIsInstance(grammar.aliases, dict)
        self.assertIsInstance(grammar.rules, dict)
        self.assertIsInstance(grammar.weights, dict)
        self.assertIsNotNone(grammar.terminal)
        self.assertEqual(grammar.terminal, "S")
        self.assertIn("N", grammar.axioms)
        self.assertIn("NP", grammar.axioms)
        self.assertIn("Adv", grammar.aliases)
        self.assertEqual(grammar.aliases["Adv"].show(), "Adv = (S / NP)")

    def test_process_axioms(self):
        grammar = CCGrammar("")
        axioms = ["S", "GrNom", "Nom"]
        grammar.process_axioms(axioms)
        self.assertEqual(len(grammar.axioms), len(axioms)-1)
        for axiom in axioms[1:]:
            self.assertIn(axiom, grammar.axioms)
        self.assertEqual(grammar.terminal, axioms[0])

    def test_process_alias(self):
        grammar = CCGrammar("")
        alias = Alias("AliasName", "AliasValue")
        grammar.process_alias(alias)

        self.assertEqual(len(grammar.aliases), 1)
        self.assertIn(alias.key, grammar.aliases)

    def test_process_judgment(self):
        grammar = CCGrammar("")
        expr = Judgement(CCGExprString("expression"), CCGTypeVar("type"))
        grammar.process_judgment(expr)

        self.assertEqual(len(grammar.rules), 1)
        self.assertIn(expr.expr.str, grammar.rules)

    def test_process_weight(self):
        grammar = CCGrammar("")
        weight = Weight("combinator_name", ["Premise1", "Premise2"], 0.5)
        grammar.process_weight(weight)

        self.assertEqual(len(grammar.weights), 1)
        self.assertIn(weight.combinator_name, grammar.weights)

    def test_process_weight_rules(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + 'cat => N' + "\n" + 'Weight("<", S/NP, NP) = 1.5'
        grammar = CCGrammar(grammar_str)
        self.assertIsNotNone(grammar.weights)
        self.assertIn("<", grammar.weights)
        self.assertIsInstance(grammar.weights["<"][0], Weight)
        self.assertEqual(grammar.weights["<"][0].combinator_name, "<")
        self.assertEqual(grammar.weights["<"][0].premices[0].show(), "(S / NP)")
        self.assertEqual(grammar.weights["<"][0].premices[1].show(), "NP")
        self.assertEqual(grammar.weights["<"][0].weight, 1.5)

    def test_expand_aliases(self):
        grammar = CCGrammar("")
        alias1 = Alias("AliasName1", CCGTypeParser("AliasValue1"))
        alias2 = Alias("AliasName2", CCGTypeParser("AliasValue2"))

        grammar.process_alias(alias1)
        grammar.process_alias(alias2)

        self.assertEqual(len(grammar.aliases), 2)
        self.assertIn(alias1.key, grammar.aliases)
        self.assertIn(alias2.key, grammar.aliases)

    def test_show(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + '"cat" => N'
        grammar = CCGrammar(grammar_str)

        self.assertIsInstance(grammar.show(), str)
        self.assertGreater(len(grammar.show()), 0)

    def test_judgement_not_match_exp(self):
        grammar = CCGrammar("")
        expr = Judgement(CCGExprString("expression"), "type")
        expr2 = Judgement(CCGExprString("expression_bis"), "type")
        self.assertIsNone(expr.match(expr2, {}))
