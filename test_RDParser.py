import unittest
from RDParser import RDParser  # Import your RDParser module

class TestRDParser(unittest.TestCase):
    def test_str_parser(self):
        parser = RDParser.str("Hello, ")
        result = parser("Hello, World!")
        self.assertEqual(result, ('Hello, ', 'World!'))

    def test_rgx_parser(self):
        parser = RDParser.rgx(r'\d+')
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, ('123', ' apples 456 oranges'))

    def test_end_parser(self):
        parser = RDParser.end()
        result = parser("Hello, World!")
        result2 = parser("")
        self.assertIsNone(result)
        self.assertEqual(result2, (None, ""))

    def test_val_parser(self):
        parser = RDParser.val("Constant")
        result = parser("Hello, World!")
        self.assertEqual(result, ('Constant', 'Hello, World!'))

    def test_seq_parser(self):
        parser = RDParser.seq(RDParser.str("Hello, "), RDParser.str("World"))
        result = parser("Hello, World!")
        self.assertEqual(result, (['Hello, ', 'World'], '!'))

    def test_alt_parser(self):
        parser = RDParser.alt(RDParser.str("Hello"), RDParser.str("Hi"))
        result = parser("Hi, there!")
        self.assertEqual(result, ('Hi', ', there!'))

    def test_mbe_parser(self):
        parser = RDParser.mbe(RDParser.str("Hello, "))
        result = parser("Hello, World!")
        self.assertEqual(result, ('Hello, ', 'World!'))

    def test_lst_parser(self):
        parser = RDParser.lst(RDParser.rgx(r'\d+'))
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, (['123'], ' apples 456 oranges'))

    def test_lst1_parser(self):
        parser = RDParser.lst1(RDParser.rgx(r'\d+'))
        result = parser("123 apples 456 oranges")
        self.assertEqual(result, (['123'], ' apples 456 oranges'))

    def test_act_parser(self):
        def double_number(result):
            return int(result) * 2

        parser = RDParser.act(RDParser.rgx(r'\d+'), double_number)
        result = parser("123 apples")
        self.assertEqual(result, (246, ' apples'))

if __name__ == '__main__':
    unittest.main()
