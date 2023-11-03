"""
Recursive Descent Monadic Parser Combinator

This class defines a Recursive Descent Monadic Parser Combinator, also known as
a Seed-Grow parser. It is a powerful tool for defining parsers for text-based
grammars. The RDParser class provides various parsing operations and
combinators that can be used to build complex parsers for natural language
processing and other text processing tasks.

Classes:
- RDParser: The main class for defining and composing parsing operations.

Methods:
- ignore(ignore, parse, str_e, mem):
  Ignore a specified portion of the input string during parsing.

- str(strg):
  Create a parsing function that matches a specific string in the input.

- rgx(regex):
  Create a parsing function that matches a regular expression in the input.

- end():
  Create a parsing function that matches the end of the input stream.

- val(val):
  Create a parsing function that returns a specified value.

- raw(_parse):
  Create a parsing function that applies a parsing operation without ignoring
  any part of the input.

- seq(*parsers):
  Create a parsing function that concatenates and sequences multiple parsing
  operations.

- alt(*parsers):
  Create a parsing function that alternates between multiple parsing
  operations.

- mbe(_parse):
  Create a parsing function that matches a parsing operation zero or one time.

- lst(_parse):
  Create a parsing function that matches a parsing operation zero or more times
  and returns a list of results.

- lst1(_parse):
  Create a parsing function that matches a parsing operation one or more times
  and returns a list of results.

- act(_parse, act):
  Create a parsing function that performs a semantics action using a specified
  function on the parsing result.

- grow(ide, _parser):
  Create a parsing function that handles left recursion for the provided
  parsing operation using memoization.

The RDParser class and its methods are valuable for defining custom parsers and
processing textual data in various natural language understanding and parsing
applications.

Example:
# Create a parser that matches and doubles numeric values in the input.
>>> double_number_parser = RDParser.act(RDParser.rgx(r'\\d+'),
                                        lambda x: int(x) * 2)
>>> result = double_number_parser("123 apples 456 oranges")
>>> print(result)
# Output: (246, ' apples 456 oranges')
"""
import re


class RDParser:
    """
    Recursive Descent Monadic Parser Combinator

    This class defines a Recursive Descent Monadic Parser Combinator
    (Seed-Grow parser) for defining the parser for grammar rules.

    Methods:
    - ignore(ignore, parse, str_e, mem): Ignore the part of the input parsed by
                                        the ignore parameter.
    - str(strg): Parse a string.
    - rgx(regex): Parse a regular expression.
    - end(): Match the end of the input stream.
    - val(val): Simply return a value.
    - raw(_parse): Skip ignore.
    - seq(*parsers): Concatenate and sequence parsers.
    - alt(*parsers): Alternation of parsers.
    - mbe(_parse): Zero or one parser.
    - lst(_parse): Zero or more parser.
    - lst1(_parse): One or more parser.
    - act(_parse, act): Semantics action.
    - grow(ide, _parser): Left recursion handling.

    The class provides a collection of methods for parsing and manipulating
    input strings using various parsing operations such as matching strings,
    regular expressions, sequencing, alternation, zero or more, one or more,
    and more. It also includes functionality for handling left recursion.

    This class is designed to help define parsers for grammar rules and is
    useful for various parsing tasks.

    Usage example:
    >>> parser = RDParser.str("Hello, ")
    >>> result = parser("Hello, World!")
    >>> print(result)
    ('Hello, ', 'World!')
    """

    @staticmethod
    def ignore(ignore, parse, str_e, mem):
        """
        Ignore the part of the input parsed by the `ignore` parameter.

        Args:
        - ignore (function): A function to specify the portion of the input to
                                ignore.
        - parse (function): The parsing operation.
        - str_e (str): The input string to be parsed.
        - mem (dict): A dictionary for memoization to optimize parsing.

        Returns:
        Tuple[Union[None, Any], str]: A tuple with the result of the parsing
                                    operation and the remaining input string.

        This function applies the 'ignore' function to the input, and if any
        part of the input is ignored, it then applies the 'parse' function to
        the remaining input and returns the result along with the modified
        input string.
        """
        ign = ignore(str_e, mem)
        if not ign:
            return None
        return parse(ign[1], mem)

    @classmethod
    def str(cls, strg):
        """
        Parse a string.

        Args:
        - strg (str): The string to match in the input.

        Returns:
        function: A parsing function.

        This method returns a parsing function that matches the provided
        'strg' in the input string.

        Example:
        >>> parser = RDParser.str("Hello, ")
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: ('Hello, ', 'World!')
        """
        strl = len(strg)

        def parse(str_e, mem={}, ignore=None):
            s = str_e[0:strl]
            if s == strg:
                return strg, str_e[strl:]
            if ignore:
                return cls.ignore(ignore, parse, str_e, mem)
            return None

        return parse

    @classmethod
    def rgx(cls, regex):
        """
        Parse a regular expression.

        Args:
        - regex (str): The regular expression pattern to match in the input.

        Returns:
        function: A parsing function.

        This method returns a parsing function that matches the provided
        regular expression pattern ('regex') in the input string.

        Example:
        >>> parser = RDParser.rgx(r'\\d+')
        >>> result = parser("123 apples")
        >>> print(result)
        # Output: ('123', ' apples')
        """
        reg = re.compile(regex)

        def parse(str_e, mem={}, ignore=None):
            m = reg.match(str_e)
            if m is not None:
                res = m.group(0)
                return res, str_e[len(res):]
            if ignore:
                return cls.ignore(ignore, parse, str_e, mem)
            return None

        return parse

    @classmethod
    def end(cls):
        """
        $ : Match the end of the input stream.

        Returns:
        function: A parsing function.

        This method returns a parsing function that matches the end of the
        input stream.

        Example:
        >>> parser = RDParser.end()
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: (None, 'Hello, World!')
        """
        def parse(str_e, mem={}, ignore=None):
            if str_e == "":
                return None, ""
            if ignore:
                return cls.ignore(ignore, parse, str_e, mem)
            return None
        return parse

    @staticmethod
    def val(val):
        """
        Simply return a value.

        Args:
        - val (Any): The value to return.

        Returns:
        function: A parsing function.

        This method returns a parsing function that simply returns the provided
        value ('val') without consuming any input.

        Example:
        >>> parser = RDParser.val("Constant")
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: ('Constant', 'Hello, World!')
        """
        def parse(str_e, mem={}, _=None):
            return val, str_e
        return parse

    @staticmethod
    def raw(_parse):
        """
        Skip ignore.

        Args:
        - _parse (function): The parsing operation.

        Returns:
        function: A parsing function.

        This method returns a parsing function that applies the provided
        parsing operation ('_parse') without ignoring any part of the input.

        Example:
        >>> parser = RDParser.raw(RDParser.str("Hello, "))
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: ('Hello, ', ' World!')
        """
        def parse(str_e, mem={}, _=None):
            return _parse(str_e, mem)
        return parse

    @staticmethod
    def seq(*parsers):
        """
        A B .. Z : Concatenate, sequence parsers.

        Args:
        - *parsers (function): Variable number of parsing operations.

        Returns:
        function: A parsing function.

        This method returns a parsing function that concatenates and sequences
        the provided parsing operations ('*parsers') in order.

        Example:
        >>> parser = RDParser.seq(RDParser.str("Hello, "),
                                  RDParser.str("World"))
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: (['Hello, ', 'World'], '!')
        """
        def parse(str_e, mem={}, ignore=None):
            idx = 0
            seq = [None for _ in parsers]
            for parse in parsers:
                res = parse(str_e, mem, ignore)
                if not res:
                    return None
                seq[idx], str_e = res
                idx = idx + 1
            return seq, str_e
        return parse

    @staticmethod
    def alt(*parsers):
        """
        A | B | ... | Z : Alternation of parsers.

        Args:
        - *parsers (function): Variable number of parsing operations.

        Returns:
        function: A parsing function.

        This method returns a parsing function that alternates between the
        provided parsing operations ('*parsers') and returns the result of the
        first successful match.

        Example:
        >>> parser = RDParser.alt(RDParser.str("Hello"), RDParser.str("Hi"))
        >>> result = parser("Hi, there!")
        >>> print(result)
        # Output: ('Hi', ', there!')
        """
        def parse(str_e, mem={}, ignore=None):
            for parse in parsers:
                res = parse(str_e, mem, ignore)
                if res:
                    return res
            return None
        return parse

    @staticmethod
    def mbe(_parse):
        """
        A? : Zero or one parser.

        Args:
        - _parse (function): The parsing operation to apply.

        Returns:
        function: A parsing function.

        This method returns a parsing function that attempts to apply the
        provided parsing operation ('_parse') and returns the result if
        successful or None if there's no match.

        Example:
        >>> parser = RDParser.mbe(RDParser.str("Hello, "))
        >>> result = parser("Hello, World!")
        >>> print(result)
        # Output: ('Hello, ', 'World!')
        """
        def parse(str_e, mem={}, ignore=None):
            res = _parse(str_e, mem, ignore)
            val = None
            if res:
                val, str_e = res
            return val, str_e
        return parse

    @staticmethod
    def lst(_parse):
        """
        A* : Zero or more parser.

        Args:
        - _parse (function): The parsing operation to apply repeatedly.

        Returns:
        function: A parsing function.

        This method returns a parsing function that applies the provided
        parsing operation ('_parse') repeatedly until there is no match,
        returning a list of all matching results.

        Example:
        >>> parser = RDParser.lst(RDParser.rgx(r'\\d+'))
        >>> result = parser("123 apples 456 oranges")
        >>> print(result)
        # Output: (['123', '456'], ' apples 456 oranges')
        """
        def parse(str_e, mem={}, ignore=None):
            idx = 0
            lst = []
            res = _parse(str_e, mem, ignore)
            while res:
                _, str_e = res
                lst.append(res[0])
                idx = idx + 1
                res = _parse(str_e, mem, ignore)
            return lst, str_e
        return parse

    @staticmethod
    def lst1(_parse):
        """
        One or more parser.

        Args:
        - _parse (function): The parsing operation to apply repeatedly.

        Returns:
        function: A parsing function.

        This method returns a parsing function that applies the provided
        parsing operation ('_parse') repeatedly at least once, returning a
        list of all matching results.

        Example:
        >>> parser = RDParser.lst1(RDParser.rgx(r'\\d+'))
        >>> result = parser("123 apples 456 oranges")
        >>> print(result)
        # Output: (['123', '456'], ' apples 456 oranges')
        """
        def parse(str_e, mem={}, ignore=None):
            idx = 0
            lst = []
            res = _parse(str_e, mem, ignore)
            while res:
                _, str_e = res
                lst.append(res[0])
                idx = idx + 1
                res = _parse(str_e, mem, ignore)
            return None if not idx else lst, str_e
        return parse

    @staticmethod
    def act(_parse, act):
        """
        Semantics action.

        Args:
        - _parse (function): The parsing operation to apply.
        - act (function): A function to perform a semantics action on
                            the result.

        Returns:
        function: A parsing function.

        This method returns a parsing function that applies the provided
        parsing operation ('_parse') and, if successful, performs a
        semantics action using the 'act' function on the result.

        Example:
        >>> def double_number(result):
        >>>     return int(result) * 2
        >>> parser = RDParser.act(RDParser.rgx(r'\\d+'), double_number)
        >>> result = parser("123 apples")
        >>> print(result)
        # Output: (246, ' apples')
        """
        def parse(str_e, mem={}, ignore=None):
            res = _parse(str_e, mem, ignore)
            if res:
                return act(res[0]), res[1]
            return None
        return parse

    @staticmethod
    def grow(ide, _parser):
        """
        Left recursion handling.

        Args:
        - ide (str): An identifier to create unique memoization keys.
        - _parser (function): The parsing operation.

        Returns:
        function: A parsing function.

        This method returns a parsing function that handles left recursion for
        the provided parsing operation ('_parser') using memoization.

        Example:
        >>> left_recursive_parser = RDParser.grow("LR",
                RDParser.seq(RDParser.raw(lazy), RDParser.str("+"),
                RDParser.raw(left_recursive_parser)))
        >>> result = left_recursive_parser("1 + 2 + 3")
        >>> print(result)
        # Output: (['1', '+', '2', '+', '3'], '')
        """

        def lazy(str_e, mem={}, ignore=None):
            return ptr[0](str_e, mem, ignore)

        def parse(str_e, mem={}, ignore=None):
            pos = len(str_e)
            uid = f"{ide}:{pos}"
            if uid in mem:
                return mem[uid]
            mem[uid] = None
            res = _parse(str_e, mem, ignore)
            while res and (not mem[uid] or len(res[1]) < len(mem[uid][1])):
                mem[uid] = res
                res = _parse(str_e, mem, ignore)
            return mem[uid]

        ptr = [None]
        _parse = _parser(lazy)
        ptr[0] = parse
        return parse
