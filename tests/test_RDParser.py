import unittest
from RDParser import RDParser as rd  # Import your rd module

class Testrd(unittest.TestCase):
    def test_str_parser(self):
        parser = rd.str("Hello, ")
        result = parser("Hello, World!")
        self.assertEqual(result, ('Hello, ', 'World!'))

    def test_rgx_parser(self):
        parser = rd.rgx(r'\d+')
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, ('123', ' apples 456 oranges'))

    def test_end_parser(self):
        parser = rd.end()
        result = parser("Hello, World!")
        result2 = parser("")
        result3 = parser("#comment", mem={}, ignore=rd.act(rd.seq(rd.str("#"), rd.rgx(".*")), lambda x: None))
        self.assertIsNone(result)
        self.assertEqual(result2, (None, ""))
        self.assertEqual(result3, (None, ""))

    def test_val_parser(self):
        parser = rd.val("Constant")
        result = parser("Hello, World!")
        self.assertEqual(result, ('Constant', 'Hello, World!'))

    def test_seq_parser(self):
        parser = rd.seq(rd.str("Hello, "), rd.str("World"))
        result = parser("Hello, World!")
        self.assertEqual(result, (['Hello, ', 'World'], '!'))

    def test_alt_parser(self):
        parser = rd.alt(rd.str("Hello"), rd.str("Hi"))
        result = parser("Hi, there!")
        self.assertEqual(result, ('Hi', ', there!'))

    def test_mbe_parser(self):
        parser = rd.mbe(rd.str("Hello, "))
        result = parser("Hello, World!")
        self.assertEqual(result, ('Hello, ', 'World!'))

    def test_lst_parser(self):
        parser = rd.lst(rd.rgx(r'\d+'))
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, (['123'], ' apples 456 oranges'))

    def test_lst1_parser(self):
        parser = rd.lst1(rd.rgx(r'\d+'))
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, (['123'], ' apples 456 oranges'))

    def test_act_parser(self):
        def double_number(result):
            return int(result) * 2

        parser = rd.act(rd.rgx(r'\d+'), double_number)
        result = parser("123 apples")
        self.assertEqual(result, (246, ' apples'))

    def test_raw_no_ignore(self):
        parser = rd.raw(rd.str("Hello, "))
        result = parser("Hello, World!")
        self.assertEqual(result, ('Hello, ', 'World!'))

    def test_raw_with_ignore(self):
        ignore_hello = (lambda x: ("Hello, ", x[len("Hello, "):]) if x.startswith("Hello, ") else (None, x))
        parser = rd.raw(rd.str("Hello"))
        result = parser("Hello World!", ignore_hello)
        self.assertEqual(result, ('Hello', ' World!'))
