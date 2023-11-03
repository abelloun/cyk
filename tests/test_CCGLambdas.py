import unittest
from CCGLambdas import (
    LambdaTerm,
    LambdaTermVar,
    LambdaTermBinop,
    LambdaTermPredicate,
    LambdaTermApplication,
    LambdaTermLambda,
    LambdaTermExists,
    show_compact,
)


class TestLambdaTerms(unittest.TestCase):
    def test_lambda_term_var(self):
        var = LambdaTermVar("x")
        self.assertEqual(var.show(), "x")

    def test_lambda_term_binop(self):
        left = LambdaTermVar("x")
        right = LambdaTermVar("y")
        binop = LambdaTermBinop("+", left, right)
        self.assertEqual(binop.show(), "(x + y)")

    def test_lambda_term_predicate(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        args = [LambdaTermVar("y"), LambdaTermVar("z")]
        predicate = LambdaTermPredicate(fun, args)
        self.assertEqual(predicate.show().strip(), "(\\x. x)(y, z)")

    def test_lambda_term_application(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        arg = LambdaTermVar("y")
        app = LambdaTermApplication(fun, arg)
        self.assertEqual(app.show().strip(), "((\\x. x) y)")

    def test_lambda_term_lambda(self):
        var = "x"
        body = LambdaTermVar("y")
        lambda_term = LambdaTermLambda(var, body)
        self.assertEqual(lambda_term.show().strip(), "(\\x. y)")

    def test_lambda_term_exists(self):
        var = "x"
        body = LambdaTermVar("y")
        exists_term = LambdaTermExists(var, body)
        self.assertEqual(exists_term.show().strip(), "(exists x. y)")

    def test_show_compact(self):
        lambda_term = LambdaTermLambda("x", LambdaTermVar("y"))
        compact_str = show_compact(lambda_term)
        self.assertEqual(compact_str.strip(), ", x. y")
