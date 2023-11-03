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

if __name__ == "__main__":
    unittest.main()
