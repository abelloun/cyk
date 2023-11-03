"""
CCG Expressions

This module defines classes for working with Combinatory Categorial Grammar
(CCG) expressions.
CCG expressions are used to represent strings of terminals and are essential
for various natural language processing tasks, such as semantic composition
and parsing.

Classes:
- CCGExpr: The base class for CCG expressions.
- CCGExprVar: Represents a variable within a CCG expression.
- CCGExprString: Represents a string literal within a CCG expression.
- CCGExprConcat: Represents the concatenation of two CCG expressions.

Each class provides methods for manipulating and working with CCG expressions.
These expressions can be variables, string literals, or combinations of both.

The module aims to facilitate the creation and manipulation of CCG expressions
for linguistic analysis and natural language processing applications.

Example:
>>> var_expr = CCGExprVar("X")
>>> str_expr = CCGExprString("apple")
>>> concat_expr = CCGExprConcat(var_expr, str_expr)
>>> print(concat_expr.show())
"X apple"
"""


class ConcatError(Exception):
    """Exception raised for errors in the concatenation.

    Attributes:
        data (CCGExpr) -- A CCG expression to match with.
        sigma (dict) -- A dictionary for variable substitution.
        message -- explanation of the error
    """

    def __init__(self, data, sigma, msg="Can't match a concatenation expr !"):
        self.data = data
        self.sigma = sigma
        self.message = msg
        super().__init__(self.message)


class CCGExpr:
    """
    Base class for CCG Expressions (strings of terminals).

    This class serves as the base for CCG expressions, which represent strings
    of terminals.

    Subclasses:
    - CCGExprVar: Represents a variable within the CCG expression.
    - CCGExprString: Represents a string literal within the CCG expression.
    - CCGExprConcat: Represents the concatenation of two CCG expressions.
    """


class CCGExprVar(CCGExpr):
    """
    Represents a variable within a CCG expression.

    This class represents a variable in a CCG expression, typically used for
    substitution and matching.

    Args:
    - name (str): The name of the variable.

    Methods:
    - show(): Return a string representation of the variable.
    - replace(sigma): Replace the variable with a value from a substitution
                        dictionary.
    - match(data, sigma): Match the variable with a data element, updating a
                            substitution dictionary.

    Example:
    >>> var_expr = CCGExprVar("X")
    >>> print(var_expr.show())
    "X"
    """

    def __init__(self, name):
        """
        Initialize a CCGExprVar object with a variable name.

        Args:
        - name (str): The name of the variable.

        Example:
        >>> var_expr = CCGExprVar("X")
        """
        self.name = name

    def show(self):
        """
        Return a string representation of the variable.

        Returns:
        str: A string representation of the variable.

        Example:
        >>> var_expr = CCGExprVar("X")
        >>> print(var_expr.show())
        "X"
        """
        return self.name

    def replace(self, sigma):
        """
        Replace the variable with a value from a substitution dictionary.

        Args:
        - sigma (dict): A dictionary that maps variable names to
                        CCG expressions.

        Returns:
        CCGExpr: The replacement CCG expression if the variable is in the
                substitution dictionary, or the original variable if not.

        Example:
        >>> var_expr = CCGExprVar("X")
        >>> substitution = {"X": CCGExprString("apple")}
        >>> replaced_expr = var_expr.replace(substitution)
        """
        return sigma[self.name] if self.name in sigma else self

    def match(self, data, sigma):
        """
        Match the variable with a data element, updating a substitution
        dictionary.

        Args:
        - data (CCGExpr): A CCG expression to match with.
        - sigma (dict): A dictionary for variable substitution.

        Returns:
        bool: True if the variable matches the data element and the
                substitution is updated, False otherwise.

        Example:
        >>> var_expr = CCGExprVar("X")
        >>> data_expr = CCGExprString("apple")
        >>> sigma = {}
        >>> result = var_expr.match(data_expr, sigma)
        >>> print(result)
        True
        >>> print(sigma)
        {"X": CCGExprString("apple")}
        """
        if self.name not in sigma:
            sigma[self.name] = data
            return True
        return sigma[self.name].match(data, None)


class CCGExprString(CCGExpr):
    """
    Represents a string literal within a CCG expression.

    This class represents a string literal within a CCG expression, such as a
    terminal string.

    Args:
    - str (str): The string literal.

    Methods:
    - __len__(): Return the length of the string literal.
    - show(): Return a string representation of the string literal.
    - replace(sigma): Replace the string literal (no-op).
    - match(data, sigma): Match the string literal with another data element.

    Example:
    >>> str_expr = CCGExprString("apple")
    >>> print(len(str_expr))
    5
    >>> print(str_expr.show())
    "apple"
    """

    def __init__(self, expr_str):
        """
        Initialize a CCGExprString object with a string literal.

        Args:
        - str (str): The string literal.

        Example:
        >>> str_expr = CCGExprString("apple")
        """
        self.str = expr_str

    def __len__(self):
        """
        Return the length of the string literal.

        Returns:
        int: The length of the string literal.

        Example:
        >>> str_expr = CCGExprString("apple")
        >>> length = len(str_expr)
        >>> print(length)
        5
        """
        return len(self.str)

    def show(self):
        """
        Return a string representation of the string literal.

        Returns:
        str: A string representation of the string literal.

        Example:
        >>> str_expr = CCGExprString("apple")
        >>> print(str_expr.show())
        "apple"
        """
        return f"\"{self.str}\""

    def replace(self, _):
        """
        Replace the string literal (no-op).

        Returns:
        CCGExprString: The original string literal.

        Example:
        >>> str_expr = CCGExprString("apple")
        >>> substitution = {"X": CCGExprString("orange")}
        >>> replaced_expr = str_expr.replace(substitution)
        """
        return self

    def match(self, data, _):
        """
        Match the string literal with another data element.

        Args:
        - data (CCGExpr): A CCG expression to match with.

        Returns:
        bool: True if the string literal matches the data element,
                False otherwise.

        Example:
        >>> str_expr = CCGExprString("apple")
        >>> data_expr = CCGExprString("apple")
        >>> sigma = {}
        >>> result = str_expr.match(data_expr, sigma)
        >>> print(result)
        True
        """
        return isinstance(data, CCGExprString) and self.str == data.str


class CCGExprConcat(CCGExpr):
    """
    Represents the concatenation of two CCG expressions.

    This class represents the concatenation of two CCG expressions,
    allowing combining expressions.

    Args:
    - left (CCGExpr): The left expression.
    - right (CCGExpr): The right expression.

    Methods:
    - __len__(): Return the total length of the concatenated expressions.
    - show(): Return a string representation of the concatenated expressions.
    - replace(sigma): Replace the concatenated expressions with values from a
                        substitution dictionary (applied recursively).
    - match(data, sigma): Raise an exception since matching a concatenation
                            expression is not supported.

    Example:
    >>> left_expr = CCGExprString("Hello")
    >>> right_expr = CCGExprString("World")
    >>> concat_expr = CCGExprConcat(left_expr, right_expr)
    >>> print(len(concat_expr))
    10
    >>> print(concat_expr.show())
    "Hello World"
    >>> substitution = {"X": CCGExprString("Goodbye")}
    >>> replaced_expr = concat_expr.replace(substitution)
    >>> print(replaced_expr.show())
    "Goodbye World"
    >>> data_expr = CCGExprString("Example")
    >>> sigma = {}
    >>> concat_expr.match(data_expr, sigma)  # This will raise an exception.
    """

    def __init__(self, left, right):
        """
        Initialize a CCGExprConcat object with two expressions.

        Args:
        - left (CCGExpr): The left expression.
        - right (CCGExpr): The right expression.

        Example:
        >>> left_expr = CCGExprString("Hello")
        >>> right_expr = CCGExprString("World")
        >>> concat_expr = CCGExprConcat(left_expr, right_expr)
        """
        self.left = left
        self.right = right

    def __len__(self):
        """
        Return the total length of the concatenated expressions.

        Returns:
        int: The combined length of the left and right expressions.

        Example:
        >>> left_expr = CCGExprString("Hello")
        >>> right_expr = CCGExprString("World")
        >>> concat_expr = CCGExprConcat(left_expr, right_expr)
        >>> length = len(concat_expr)
        >>> print(length)
        10
        """
        return len(self.left) + len(self.right)

    def show(self):
        """
        Return a string representation of the concatenated expressions.

        Returns:
        str: A string representation of the concatenated expressions.

        Example:
        >>> left_expr = CCGExprString("Hello")
        >>> right_expr = CCGExprString("World")
        >>> concat_expr = CCGExprConcat(left_expr, right_expr)
        >>> print(concat_expr.show())
        "Hello World"
        """
        return f"{self.left.show()[:-1]} {self.right.show()[1:]}"

    def replace(self, sigma):
        """
        Replace the concatenated expressions with values from a substitution
        dictionary (applied recursively).

        Args:
        - sigma (dict): A dictionary that maps variable names to CCG
                        expressions.

        Returns:
        CCGExprConcat: A new concatenated expression with replaced left and
                        right expressions.

        Example:
        >>> left_expr = CCGExprVar("X")
        >>> right_expr = CCGExprVar("Y")
        >>> concat_expr = CCGExprConcat(left_expr, right_expr)
        >>> substitution = {"X": CCGExprString("Goodbye"),
                            "Y": CCGExprString("World")}
        >>> replaced_expr = concat_expr.replace(substitution)
        >>> print(replaced_expr.show())
        "Goodbye World"
        """
        lrep = self.left.replace(sigma)
        rrep = self.right.replace(sigma)
        return CCGExprConcat(lrep, rrep)

    def match(self, data, sigma):
        """
        Raise an exception since matching a concatenation expression is
        not supported.

        Args:
        - data (CCGExpr): A CCG expression to match with.
        - sigma (dict): A dictionary for variable substitution.

        Raises:
        Exception: Matching a concatenation expression is not supported.

        Example:
        >>> left_expr = CCGExprString("Hello")
        >>> right_expr = CCGExprString("World")
        >>> concat_expr = CCGExprConcat(left_expr, right_expr)
        >>> data_expr = CCGExprString("Example")
        >>> sigma = {}
        >>> concat_expr.match(data_expr, sigma) # This will raise an exception.
        """
        raise ConcatError(data, sigma)
