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

    def test_fresh(self):
        f1 = LambdaTerm.fresh("X")
        self.assertIsInstance(f1, str)
        f2 = LambdaTerm.fresh("X")
        self.assertIsInstance(f2, str)
        self.assertNotEqual(f1, f2)

    def test_reset(self):
        LambdaTerm.reset()
        f1 = LambdaTerm.fresh("X")
        LambdaTerm.reset()
        f2 = LambdaTerm.fresh("X")
        self.assertIsInstance(f1, str)
        self.assertIsInstance(f2, str)
        self.assertEqual(f1, f2)

    def test_lambda_eval(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        v = LambdaTermVar("Q")
        env = {"P" : v}
        self.assertEqual(v1.eval(env), v)
        self.assertNotEqual(v1, v)
        self.assertEqual(v2.eval(env), v2)

    def test_lambdabinop_eval(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        v = LambdaTermVar("Q")
        vs = LambdaTermVar("U")
        vb = LambdaTermBinop("&", v1, v2)
        vbf = LambdaTermBinop("&", v1, v)

        env = {"P" : v, "T" : vs}

        res = LambdaTermBinop("&", v, vs)
        res2 = LambdaTermBinop("&", v, v)
        self.assertEqual(vb.eval(env).show(), res.show())
        self.assertNotEqual(vb.show(), res.show())
        self.assertEqual(vbf.eval(env).show(), res2.show())

    def test_lambda_apply(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        res = v1.apply(v2)
        self.assertEqual(res.show(), LambdaTermApplication(v1, v2).show())

    def test_lambdabinop_apply(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        v = LambdaTermVar("Q")
        vs = LambdaTermVar("U")
        vb = LambdaTermBinop("&", v1, v2)
        res = vb.apply(v)
        self.assertEqual(res.show(), LambdaTermBinop("&", LambdaTermApplication(v1, v), LambdaTermApplication(v2, v)).show())
        self.assertNotEqual(vb.show(), res.show())

    def test_lambda_apply_predicate(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        v3 = LambdaTermVar("Q")
        res = v1.apply_predicate([v2, v3])
        self.assertEqual(res.show(), LambdaTermPredicate(v1, [v2, v3]).show())

    def test_lambdabinop_apply_predicate(self):
        v1 = LambdaTermVar("P")
        v2 = LambdaTermVar("T")
        v = LambdaTermVar("Q")
        vs = LambdaTermVar("U")
        vb = LambdaTermBinop("&", v1, v2)
        res = vb.apply_predicate([v, vs])
        self.assertEqual(res.show(), LambdaTermBinop("&", LambdaTermPredicate(v1, [v, vs]), LambdaTermPredicate(v2, [v, vs])).show())
        self.assertNotEqual(vb.show(), res.show())

    def test_lambda_predicate_eval(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        args = [LambdaTermVar("y"), LambdaTermVar("z")]
        predicate = LambdaTermPredicate(fun, args)

        env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        result = predicate.eval(env)

        expected_result = LambdaTermPredicate(LambdaTermVar("w"), [LambdaTermVar("z")])
        self.assertEqual(result.show(), expected_result.show())

    def test_lambda_predicate_apply(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        args = [LambdaTermVar("y")]
        predicate = LambdaTermPredicate(fun, args)

        new_arg = LambdaTermVar("z")
        updated_predicate = predicate.apply(new_arg)

        expected_result = LambdaTermPredicate(fun, [LambdaTermVar("y"), LambdaTermVar("z")])
        self.assertEqual(updated_predicate.show(), expected_result.show())

    def test_lambda_predicate_apply_predicate(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        args = [LambdaTermVar("y")]
        predicate = LambdaTermPredicate(fun, args)

        additional_args = [LambdaTermVar("z"), LambdaTermVar("w")]
        updated_predicate = predicate.apply_predicate(additional_args)

        expected_result = LambdaTermPredicate(fun, [LambdaTermVar("y"), LambdaTermVar("z"), LambdaTermVar("w")])
        self.assertEqual(updated_predicate.show(), expected_result.show())

    def test_lambda_application_eval(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        arg = LambdaTermVar("y")
        app = LambdaTermApplication(fun, arg)

        env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        result = app.eval(env)

        expected_result = LambdaTermVar("w")
        self.assertEqual(result.show(), expected_result.show())

    def test_lambda_application_apply(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        arg = LambdaTermVar("y")
        app = LambdaTermApplication(fun, arg)

        new_arg = LambdaTermVar("z")
        updated_app = app.apply(new_arg)

        expected_result = LambdaTermApplication(LambdaTermApplication(LambdaTermLambda("x", LambdaTermVar("x")), LambdaTermVar("y")), LambdaTermVar("z"))
        self.assertEqual(updated_app.show(), expected_result.show())

    def test_lambda_application_apply_predicate(self):
        fun = LambdaTermLambda("x", LambdaTermVar("x"))
        arg = LambdaTermVar("y")
        app = LambdaTermApplication(fun, arg)

        predicate_args = [LambdaTermVar("z"), LambdaTermVar("w")]
        predicate_app = app.apply_predicate(predicate_args)

        expected_result = LambdaTermPredicate(app, predicate_args)
        self.assertEqual(predicate_app.show(), expected_result.show())

    def test_lambda_exists_build(self):
        exists_term = LambdaTermExists.build(LambdaTermVar("y"), "z")

        expected_result = LambdaTermExists("z", LambdaTermVar("y"))
        self.assertEqual(exists_term.show(), expected_result.show())

    def test_lambda_lambda_build(self):
        exists_term = LambdaTermLambda.build(LambdaTermVar("y"), "z")

        expected_result = LambdaTermLambda("z", LambdaTermVar("y"))
        self.assertEqual(exists_term.show(), expected_result.show())

    def test_lambda_exists_eval(self):
        var = "x"
        body = LambdaTermVar("y")
        exists_term = LambdaTermExists(var, body)

        env = {"s": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        evaluated_term = exists_term.eval(env)
        expected_result = LambdaTermExists("x", LambdaTermVar("w"))
        self.assertEqual(evaluated_term.body.show(), expected_result.body.show())

    def test_lambda_exists_apply(self):
        var = "x"
        body = LambdaTermVar("y")
        exists_term = LambdaTermExists(var, body)

        arg = LambdaTermVar("z")
        result = exists_term.apply(arg)

        expected_result = body.eval({var: arg})
        self.assertEqual(result.show(), expected_result.show())

    def test_lambda_exists_apply_predicate(self):
        var = "x"
        body = LambdaTermVar("y")
        exists_term = LambdaTermExists(var, body)

        args = [LambdaTermVar("z"), LambdaTermVar("w")]
        result_predicate = exists_term.apply_predicate(args)
        expected_result = body.eval({var: args[0]}).apply_predicate(args[1:])
        self.assertEqual(result_predicate.show(), expected_result.show())
