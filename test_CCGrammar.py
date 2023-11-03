import unittest
from CCGrammar import CCGrammar, Alias, Judgement, Weight, CCGExprString, CCGTypeParser

class TestCCGrammar(unittest.TestCase):

    def test_parse(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + '"cat" => N'
        parsed_statements = CCGrammar.parse(grammar_str)

        self.assertTrue(isinstance(parsed_statements, list))
        self.assertGreater(len(parsed_statements), 0)

    def test_init(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + '"cat" => N'
        grammar = CCGrammar(grammar_str)

        self.assertIsInstance(grammar.axioms, dict)
        self.assertIsInstance(grammar.aliases, dict)
        self.assertIsInstance(grammar.rules, dict)
        self.assertIsInstance(grammar.weights, dict)
        self.assertIsNotNone(grammar.terminal)

    def test_process_axioms(self):
        grammar = CCGrammar("")
        axioms = ["Nom[Masc]", "Nom[Fem]", ""]
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
        expr = Judgement(CCGExprString("expression"), "type")
        grammar.process_judgment(expr)

        self.assertEqual(len(grammar.rules), 1)
        self.assertIn(expr.expr.str, grammar.rules)

    def test_process_weight(self):
        grammar = CCGrammar("")
        weight = Weight("combinator_name", ["Premise1", "Premise2"], 0.5)
        grammar.process_weight(weight)

        self.assertEqual(len(grammar.weights), 1)
        self.assertIn(weight.combinator_name, grammar.weights)

    def test_expand_aliases(self):
        grammar = CCGrammar("")
        alias1 = Alias("AliasName1", CCGTypeParser("AliasValue1"))
        alias2 = Alias("AliasName2", CCGTypeParser("AliasValue2"))

        grammar.process_alias(alias1)
        grammar.process_alias(alias2)
        # grammar.expand_aliases()

        self.assertEqual(len(grammar.aliases), 2)
        self.assertIn(alias1.key, grammar.aliases)
        self.assertIn(alias2.key, grammar.aliases)

    def test_show(self):
        grammar_str = ":- S, N, NP" + "\n" + "Adv :: S/NP" + "\n" + '"cat" => N'
        grammar = CCGrammar(grammar_str)

        self.assertIsInstance(grammar.show(), str)
        self.assertGreater(len(grammar.show()), 0)

if __name__ == '__main__':
    unittest.main()
