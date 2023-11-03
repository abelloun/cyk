import unittest
from CCGExprs import CCGExpr, CCGExprVar, CCGExprString, CCGExprConcat, ConcatError

class TestCCGExpressions(unittest.TestCase):

    def test_ccg_expr_var(self):
        var_expr = CCGExprVar("X")
        self.assertEqual(var_expr.show(), "X")

    def test_ccg_expr_string(self):
        str_expr = CCGExprString("apple")
        self.assertEqual(len(str_expr), 5)
        self.assertEqual(str_expr.show(), "\"apple\"")

    def test_ccg_expr_concat(self):
        left_expr = CCGExprString("Hello")
        right_expr = CCGExprString("World")
        concat_expr = CCGExprConcat(left_expr, right_expr)

        self.assertEqual(len(concat_expr), 10)
        self.assertEqual(concat_expr.show(), "\"Hello World\"")

    def test_ccg_expr_concat_replace(self):
        left_expr = CCGExprVar("X")
        right_expr = CCGExprVar("Y")
        concat_expr = CCGExprConcat(left_expr, right_expr)
        substitution = {"X": CCGExprString("Goodbye"), "Y": CCGExprString("World")}
        replaced_expr = concat_expr.replace(substitution)

        self.assertEqual(replaced_expr.show(), "\"Goodbye World\"")

    def test_ccg_expr_var_match(self):
        var_expr = CCGExprVar("X")
        data_expr = CCGExprString("apple")
        sigma = {}
        result = var_expr.match(data_expr, sigma)

        self.assertTrue(result)
        # Compare string representations of objects
        self.assertEqual(data_expr.show(), sigma["X"].show())

    def test_ccg_expr_concat_match(self):
        left_expr = CCGExprString("Hello")
        right_expr = CCGExprString("World")
        concat_expr = CCGExprConcat(left_expr, right_expr)
        data_expr = CCGExprString("Example")
        sigma = {}

        with self.assertRaises(ConcatError):
            concat_expr.match(data_expr, sigma)

    def test_match_and_replace(self):
        var_expr = CCGExprVar("X")
        data_expr = CCGExprString("apple")
        sigma = {}

        # Test initial match
        result = var_expr.match(data_expr, sigma)
        self.assertTrue(result)
        self.assertEqual({k: v.show() for k, v in sigma.items()}, {"X": CCGExprString("apple").show()})

        # Test re-match with different data
        data_expr2 = CCGExprString("banana")
        sigma = {}  # Reset the substitution dictionary
        result = var_expr.match(data_expr2, sigma)
        self.assertTrue(result)
        self.assertEqual({k: v.show() for k, v in sigma.items()}, {"X": CCGExprString("banana").show()})

        # Test re-match with same data
        sigma = {}  # Reset the substitution dictionary
        result = var_expr.match(data_expr, sigma)
        self.assertTrue(result)
        self.assertEqual({k: v.show() for k, v in sigma.items()}, {"X": CCGExprString("apple").show()})

    def test_replace_with_substitution(self):
        var_expr = CCGExprVar("X")
        substitution = {"X": CCGExprString("apple")}

        # Test replacing with substitution
        replaced_expr = var_expr.replace(substitution)
        self.assertEqual(replaced_expr.show(), CCGExprString("apple").show())

        # Test replacing with an empty substitution
        sigma = {}  # Reset the substitution dictionary
        replaced_expr = var_expr.replace(sigma)
        self.assertEqual(replaced_expr, var_expr)

    def test_match_return_value(self):
        var_expr = CCGExprVar("X")
        data_expr = CCGExprString("apple")
        sigma = {}

        # Ensure the return value of match is True
        result = var_expr.match(data_expr, sigma)
        self.assertTrue(result)

    def test_match_with_existing_variable(self):
        var_expr = CCGExprVar("X")
        data_expr = CCGExprString("apple")
        sigma = {"X": CCGExprString("banana")}

        # Ensure that when self.name is in sigma, it matches the data but doesn't update sigma
        result = var_expr.match(data_expr, sigma)
        self.assertFalse(result)
        self.assertEqual({k: v.show() for k, v in sigma.items()}, {"X": CCGExprString("banana").show()})
