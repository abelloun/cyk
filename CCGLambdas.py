"""
Lambda Terms and Lambda Calculus Parser

This module provides classes and functions for working with lambda
calculus terms, including lambda abstractions, variable terms,
binary operations, predicate applications, and existential quantifications.
It also offers methods for parsing, displaying, evaluating,
and applying lambda terms within the context of lambda calculus.

Classes:
- `LambdaTerm`: The base class for lambda calculus terms, offering common
                functionality.
- `LambdaTermVar`: Represents a variable lambda term.
- `LambdaTermBinop`: Represents a binary operation between two lambda terms.
- `LambdaTermPredicate`: Represents a predicate application term.
- `LambdaTermApplication`: Represents a lambda term application.
- `LambdaTermLambda`: Represents a lambda abstraction term.
- `LambdaTermExists`: Represents an existential quantification term.

Functions:
- `show_compact`: Utilitary to generate a compact string representation
                    of a lambda term.

Example:
    >>> var = "x"
    >>> body = LambdaTermVar("y")
    >>> exists_term = LambdaTermExists(var, body)
    >>> print(exists_term.show())
    >>> evaluated_term = exists_term.eval(env)
    >>> result = exists_term.apply(arg)
    >>> result_predicate = exists_term.apply_predicate(args)
"""


class LambdaTerm:
    """
    Base class for lambda calculus terms.

    This class serves as the base class for various lambda calculus terms
    and provides common functionality for lambda terms.

    Class Attributes:
    - count (int): A class-level counter used for generating fresh
                    variable names.

    Example:
    >>> term = LambdaTerm()
    """
    count = -1

    @classmethod
    def fresh(cls, var):
        """
        Generate a fresh variable name based on the input variable.

        This method generates a fresh variable name by appending a
        unique number to the base variable name.

        Args:
        - var (str): The base variable name.

        Returns:
        str: A fresh variable name.

        Example:
        >>> base_var = "x"
        >>> fresh_var = LambdaTerm.fresh(base_var)
        """
        cls.count += 1
        return f"{var.split('_')[0]}_{cls.count}"

    @classmethod
    def reset(cls):
        """
        Reset the class-level counter for generating fresh variable names.

        This method resets the class-level counter to its initial state,
        allowing fresh variable names to be generated from scratch.

        Example:
        >>> LambdaTerm.reset()
        """
        cls.count = -1


class LambdaTermVar(LambdaTerm):
    """
    Represents a variable lambda term.

    This class defines a lambda term that represents a variable. It can be
    used in lambda calculus expressions and can be evaluated in an environment.

    Args:
    - name (str): The name of the variable.

    Example:
    >>> variable = LambdaTermVar("x")
    """

    def __init__(self, name):
        """
        Initialize a LambdaTermVar object with a variable name.

        Args:
        - name (str): The name of the variable.

        Example:
        >>> variable = LambdaTermVar("x")
        """
        self.name = name

    def show(self):
        """
        Generate a string representation of the variable.

        Returns:
        str: A string representation of the variable.

        Example:
        >>> variable = LambdaTermVar("x")
        >>> print(variable.show())
        "x"
        """
        return self.name

    def eval(self, env):
        """
        Evaluate the variable in a given environment.

        Args:
        - env (dict): The environment for variable bindings.

        Returns:
        LambdaTerm: The result of evaluating the variable in the environment.

        Example:
        >>> env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        >>> variable = LambdaTermVar("x")
        >>> result = variable.eval(env)
        """
        return env[self.name] if self.name in env else self

    def apply(self, arg):
        """
        Apply another lambda term as an argument to the variable.

        Args:
        - arg (LambdaTerm): The argument lambda term to apply.

        Returns:
        LambdaTermApplication: A new lambda term representing the application
        of the variable to the argument.

        Example:
        >>> variable = LambdaTermVar("x")
        >>> argument = LambdaTermVar("y")
        >>> application = variable.apply(argument)
        """
        return LambdaTermApplication(self, arg)

    def apply_predicate(self, args):
        """
        Apply additional predicate arguments to the variable.

        Args:
        - args (list): A list of additional predicate arguments.

        Returns:
        LambdaTermPredicate: A new lambda term representing the application
        of the variable as a predicate with additional arguments.

        Example:
        >>> variable = LambdaTermVar("x")
        >>> additional_args = [LambdaTermVar("y"), LambdaTermVar("z")]
        >>> predicate = variable.apply_predicate(additional_args)
        """
        return LambdaTermPredicate(self, args)


class LambdaTermBinop(LambdaTerm):
    """
    Represents a binary operation between two lambda terms.

    This class defines a lambda term that represents a binary operation between
    two other lambda terms.
    It allows the evaluation and application of binary operations.

    Args:
    - op (str): The binary operation symbol.
    - left (LambdaTerm): The left operand lambda term.
    - right (LambdaTerm): The right operand lambda term.

    Example:
    >>> left_operand = LambdaTermVar("x")
    >>> right_operand = LambdaTermVar("y")
    >>> binop = LambdaTermBinop("+", left_operand, right_operand)
    """

    def __init__(self, op, left, right):
        """
        Initialize a LambdaTermBinop object with a binary operation
        and two operands.

        Args:
        - op (str): The binary operation symbol.
        - left (LambdaTerm): The left operand lambda term.
        - right (LambdaTerm): The right operand lambda term.
        """
        self.op = op
        self.left = left
        self.right = right

    def show(self):
        """
        Generate a string representation of the binary operation.

        Returns:
        str: A string representation of the binary operation.

        Example:
        >>> left_operand = LambdaTermVar("x")
        >>> right_operand = LambdaTermVar("y")
        >>> binop = LambdaTermBinop("+", left_operand, right_operand)
        >>> print(binop.show())
        "(x + y)"
        """
        return f"({self.left.show()} {self.op} {self.right.show()})"

    def eval(self, env):
        """
        Evaluate the binary operation in a given environment.

        Args:
        - env (dict): The environment for variable bindings.

        Returns:
        LambdaTermBinop: The result of evaluating the binary operation.

        Example:
        >>> env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        >>> left_operand = LambdaTermVar("x")
        >>> right_operand = LambdaTermVar("y")
        >>> binop = LambdaTermBinop("+", left_operand, right_operand)
        >>> result = binop.eval(env)
        """
        leval = self.left.eval(env)
        reval = self.right.eval(env)
        return LambdaTermBinop(self.op, leval, reval)

    def apply(self, arg):
        """
        Apply a new argument to both operands of the binary operation.

        Args:
        - arg (LambdaTerm): The argument lambda term to apply.

        Returns:
        LambdaTermBinop: A new binary operation with the added argument applied
                        to both operands.

        Example:
        >>> left_operand = LambdaTermVar("x")
        >>> right_operand = LambdaTermVar("y")
        >>> binop = LambdaTermBinop("+", left_operand, right_operand)
        >>> new_arg = LambdaTermVar("z")
        >>> updated_binop = binop.apply(new_arg)
        """
        lapp = self.left.apply(arg)
        rapp = self.right.apply(arg)
        return LambdaTermBinop(self.op, lapp, rapp)

    def apply_predicate(self, args):
        """
        Apply additional predicate arguments to both operands of the binary
        operation.

        Args:
        - args (list): A list of additional predicate arguments.

        Returns:
        LambdaTermBinop: A new binary operation with the added arguments
        applied to both operands.

        Example:
        >>> left_operand = LambdaTermVar("x")
        >>> right_operand = LambdaTermVar("y")
        >>> binop = LambdaTermBinop("+", left_operand, right_operand)
        >>> additional_args = [LambdaTermVar("z"), LambdaTermVar("w")]
        >>> updated_binop = binop.apply_predicate(additional_args)
        """
        lapp = self.left.apply_predicate(args)
        rapp = self.right.apply_predicate(args)
        return LambdaTermBinop(self.op, lapp, rapp)


class LambdaTermPredicate(LambdaTerm):
    """
    Represents a predicate application.

    This class defines a lambda term that represents the application of
    a predicate function to a list of arguments. It allows the evaluation and
    application of predicate functions with arguments.

    Args:
    - fun (LambdaTerm): The predicate function.
    - args (list): A list of lambda terms representing predicate arguments.

    Example:
    >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
    >>> args = [LambdaTermVar("y"), LambdaTermVar("z")]
    >>> predicate = LambdaTermPredicate(fun, args)
    """

    def __init__(self, fun, args):
        """
        Initialize a LambdaTermPredicate object with a predicate function and
        arguments.

        Args:
        - fun (LambdaTerm): The predicate function.
        - args (list): A list of lambda terms representing predicate arguments.
        """
        self.fun = fun
        self.args = args

    def show(self):
        """
        Generate a string representation of the predicate application.

        Returns:
        str: A string representation of the predicate application.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> args = [LambdaTermVar("y"), LambdaTermVar("z")]
        >>> predicate = LambdaTermPredicate(fun, args)
        >>> print(predicate.show())
        "(\\x . x)(y, z)"
        """
        args = ", ".join([arg.show() for arg in self.args])
        return f"{self.fun.show()}({args})"

    def eval(self, env):
        """
        Evaluate the predicate application in a given environment.

        Args:
        - env (dict): The environment for variable bindings.

        Returns:
        LambdaTermPredicate: The result of evaluating the predicate
                                application.

        Example:
        >>> env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> args = [LambdaTermVar("y"), LambdaTermVar("x")]
        >>> predicate = LambdaTermPredicate(fun, args)
        >>> result = predicate.eval(env)
        """
        evargs = [arg.eval(env) for arg in self.args]
        return self.fun.eval(env).apply_predicate(evargs)

    def apply(self, arg):
        """
        Apply a new argument to the predicate application.

        Args:
        - arg (LambdaTerm): The argument lambda term to apply.

        Returns:
        LambdaTermPredicate: A new predicate application with the added
                            argument.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> args = [LambdaTermVar("y")]
        >>> predicate = LambdaTermPredicate(fun, args)
        >>> new_arg = LambdaTermVar("z")
        >>> updated_predicate = predicate.apply(new_arg)
        """
        return LambdaTermPredicate(self.fun, self.args + [arg])

    def apply_predicate(self, args):
        """
        Apply additional predicate arguments to the current predicate
        application.

        Args:
        - args (list): A list of additional predicate arguments.

        Returns:
        LambdaTermPredicate: A new predicate application with the added
                            arguments.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> args = [LambdaTermVar("y")]
        >>> predicate = LambdaTermPredicate(fun, args)
        >>> additional_args = [LambdaTermVar("z"), LambdaTermVar("w")]
        >>> updated_predicate = predicate.apply_predicate(additional_args)
        """
        return LambdaTermPredicate(self.fun, self.args + args)


class LambdaTermApplication(LambdaTerm):
    """
    Represents a lambda term application.

    This class defines a lambda term that represents the application of one
    lambda term to another. It allows evaluation and application of
    lambda terms.

    Args:
    - fun (LambdaTerm): The function part of the application.
    - arg (LambdaTerm): The argument part of the application.

    Example:
    >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
    >>> arg = LambdaTermVar("y")
    >>> app = LambdaTermApplication(fun, arg)
    """

    def __init__(self, fun, arg):
        """
        Initialize a LambdaTermApplication object with a function and
        an argument.

        Args:
        - fun (LambdaTerm): The function part of the application.
        - arg (LambdaTerm): The argument part of the application.
        """
        self.fun = fun
        self.arg = arg

    def show(self):
        """
        Generate a string representation of the lambda term application.

        Returns:
        str: A string representation of the lambda term application.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> arg = LambdaTermVar("y")
        >>> app = LambdaTermApplication(fun, arg)
        >>> print(app.show())
        "(\\x . x) y"
        """
        return f"({self.fun.show()} {self.arg.show()})"

    def eval(self, env):
        """
        Evaluate the lambda term application in a given environment.

        Args:
        - env (dict): The environment for variable bindings.

        Returns:
        LambdaTerm: The result of evaluating the lambda term application.

        Example:
        >>> env = {"x": LambdaTermVar("z"), "y": LambdaTermVar("w")}
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> arg = LambdaTermVar("y")
        >>> app = LambdaTermApplication(fun, arg)
        >>> result = app.eval(env)
        """
        return self.fun.eval(env).apply(self.arg.eval(env))

    def apply(self, arg):
        """
        Apply a lambda term as an argument to the current application.

        Args:
        - arg (LambdaTerm): The argument lambda term to apply.

        Returns:
        LambdaTermApplication: A new lambda term application with the updated
                                argument.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> arg = LambdaTermVar("y")
        >>> app = LambdaTermApplication(fun, arg)
        >>> new_arg = LambdaTermVar("z")
        >>> updated_app = app.apply(new_arg)
        """
        return LambdaTermApplication(self, arg)

    def apply_predicate(self, args):
        """
        Apply predicate arguments to the current application.

        Args:
        - args (list): A list of predicate arguments.

        Returns:
        LambdaTermPredicate: A lambda term representing a predicate
                            application.

        Example:
        >>> fun = LambdaTermLambda("x", LambdaTermVar("x"))
        >>> arg = LambdaTermVar("y")
        >>> app = LambdaTermApplication(fun, arg)
        >>> predicate_args = [LambdaTermVar("z"), LambdaTermVar("w")]
        >>> predicate_app = app.apply_predicate(predicate_args)
        """
        return LambdaTermPredicate(self, args)


def show_compact(lamb):
    """
    Generate a compact string representation of a lambda term.

    This function takes a lambda term as input and generates a compact
    string representation by recursively concatenating variable names in the
    case of lambda abstractions and showing the lambda term when it's not a
    lambda abstraction.

    Args:
    - lamb (LambdaTerm): The lambda term to represent compactly.

    Returns:
    str: A compact string representation of the lambda term.

    Example:
    >>> lambda_term = LambdaTermLambda("x", LambdaTermVar("y"))
    >>> compact_str = show_compact(lambda_term)
    >>> print(compact_str)
    ", x . y"
    """
    if isinstance(lamb, LambdaTermLambda):
        return ", " + str(lamb.var) + show_compact(lamb.body)
    return ". " + lamb.show()


class LambdaTermLambda(LambdaTerm):
    """
    Represents a lambda term that represents a lambda abstraction.

    This class extends the LambdaTerm class to represent a lambda abstraction
    lambda term.
    It provides methods for displaying, evaluating, and applying the term.

    Attributes:
    - var (str): The variable used in the lambda abstraction.
    - body (LambdaTerm): The body of the lambda abstraction.

    Methods:
    - show(): Generate a string representation of the lambda abstraction term.
    - eval(env): Evaluate the lambda abstraction term in an environment.
    - apply(arg): Apply the lambda abstraction term to an argument.
    - apply_predicate(args): Apply the lambda abstraction term as a
                            predicate to a list of arguments.

    Example:
    >>> var = "x"
    >>> body = LambdaTermVar("y")
    >>> lambda_term = LambdaTermLambda(var, body)
    >>> print(lambda_term.show())
    >>> evaluated_term = lambda_term.eval(env)
    >>> result = lambda_term.apply(arg)
    >>> result_predicate = lambda_term.apply_predicate(args)
    """

    @classmethod
    def build(cls, u, v):
        """
        Build a lambda abstraction term from variables u and v.

        Args:
        - u (str): The variable u.
        - v (str): The variable v.

        Returns:
        LambdaTermLambda: A lambda abstraction term.

        Example:
        >>> lambda_term = LambdaTermLambda.build("x", "y")
        """
        return cls(v, u)

    def __init__(self, var, body):
        """
        Initialize a lambda abstraction term with the provided variable
        and body.

        Args:
        - var (str): The variable used in the lambda abstraction.
        - body (LambdaTerm): The body of the lambda abstraction.

        Example:
        >>> var = "x"
        >>> body = LambdaTermVar("y")
        >>> lambda_term = LambdaTermLambda(var, body)
        """
        self.var = var
        self.body = body

    def show(self):
        """
        Generate a string representation of the lambda abstraction term.

        Returns:
        str: A string representation of the lambda abstraction term.

        Example:
        >>> print(lambda_term.show())
        """
        return f"(\\{show_compact(self)[2:]})"

    def eval(self, env):
        """
        Evaluate the lambda abstraction term in an environment.

        Args:
        - env (dict): The environment with variable bindings.

        Returns:
        LambdaTermLambda: The evaluated lambda abstraction term.

        Example:
        >>> evaluated_term = lambda_term.eval(env)
        """
        v = self.fresh(self.var)
        envt = {**env, self.var: LambdaTermVar(v)}
        return LambdaTermLambda(v, self.body.eval(envt))

    def apply(self, arg):
        """
        Apply the lambda abstraction term to an argument.

        Args:
        - arg (LambdaTerm): The argument to apply to the term.

        Returns:
        LambdaTerm: The result of applying the term to the argument.

        Example:
        >>> result = lambda_term.apply(arg)
        """
        self.reset()
        return self.body.eval({self.var: arg})

    def apply_predicate(self, args):
        """
        Apply the lambda abstraction term as a predicate to a list of
        arguments.

        Args:
        - args (list): A list of arguments to apply to the term.

        Returns:
        LambdaTerm: The result of applying the term as a predicate to the
                    arguments.

        Example:
        >>> result_predicate = lambda_term.apply_predicate(args)
        """
        f = self.body.eval({self.var: args[0]})
        return f.apply_predicate(args[1:]) if len(args) > 1 else f


class LambdaTermExists(LambdaTerm):
    """
    Represents a lambda term that represents existential quantification.

    This class extends the LambdaTerm class to represent an existential
    quantification lambda term.
    It provides methods for displaying, evaluating, and applying the term.

    Attributes:
    - var (str): The variable being quantified.
    - body (LambdaTerm): The body of the existential quantification.

    Methods:
    - show(): Generate a string representation of the existential
                quantification term.
    - eval(env): Evaluate the existential quantification term in an
                    environment.
    - apply(arg): Apply the term to an argument.
    - apply_predicate(args): Apply the term as a predicate to a list of
                            arguments.

    Example:
    >>> var = "x"
    >>> body = LambdaTermVar("y")
    >>> exists_term = LambdaTermExists(var, body)
    >>> print(exists_term.show())
    >>> evaluated_term = exists_term.eval(env)
    >>> result = exists_term.apply(arg)
    >>> result_predicate = exists_term.apply_predicate(args)
    """

    @classmethod
    def build(cls, u, v):
        """
        Build an existential quantification term from variables u and v.

        Args:
        - u (str): The variable u.
        - v (str): The variable v.

        Returns:
        LambdaTermExists: An existential quantification term.

        Example:
        >>> exists_term = LambdaTermExists.build("x", "y")
        """
        return cls(v, u)

    def __init__(self, var, body):
        """
        Initialize an existential quantification term with the provided
        variable and body.

        Args:
        - var (str): The variable being quantified.
        - body (LambdaTerm): The body of the existential quantification.

        Example:
        >>> var = "x"
        >>> body = LambdaTermVar("y")
        >>> exists_term = LambdaTermExists(var, body)
        """
        self.var = var
        self.body = body

    def show(self):
        """
        Generate a string representation of the existential quantification
        term.

        Returns:
        str: A string representation of the existential quantification term.

        Example:
        >>> print(exists_term.show())
        """
        return f"(exists {self.var}. {self.body.show()})"

    def eval(self, env):
        """
        Evaluate the existential quantification term in an environment.

        Args:
        - env (dict): The environment with variable bindings.

        Returns:
        LambdaTermExists: The evaluated existential quantification term.

        Example:
        >>> evaluated_term = exists_term.eval(env)
        """
        v = self.fresh(self.var)
        envt = {**env, self.var: LambdaTermVar(v)}
        return LambdaTermExists(v, self.body.eval(envt))

    def apply(self, arg):
        """
        Apply the existential quantification term to an argument.

        Args:
        - arg (LambdaTerm): The argument to apply to the term.

        Returns:
        LambdaTerm: The result of applying the term to the argument.

        Example:
        >>> result = exists_term.apply(arg)
        """
        return self.body.eval({self.var: arg})

    def apply_predicate(self, args):
        """
        Apply the existential quantification term as a predicate to a list of
        arguments.

        Args:
        - args (list): A list of arguments to apply to the term.

        Returns:
        LambdaTerm: The result of applying the term as a predicate to the
                    arguments.

        Example:
        >>> result_predicate = exists_term.apply_predicate(args)
        """
        f = self.body.eval({self.var: args[0]})
        return f.apply_predicate(args[1:]) if len(args) > 1 else f
