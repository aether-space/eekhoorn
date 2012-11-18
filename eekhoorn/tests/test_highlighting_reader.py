import unittest

from sqlparse import tokens
from sqlparse.sql import Token

from eekhoorn.highlighting_reader import group_by_line


Text = tokens.Token.Text

class Test(unittest.TestCase):
    def test_group_by_line(self):
        tokens = [Token(Text, "foo"), Token(Text, "bar\nrab")]
        result = []
        for line in group_by_line(tokens):
            result.append([(t.ttype, t.value) for t in line])
        expected = [
            [(Text, "foo"), (Text, "bar")],
            [(Text, "rab")]
        ]
        self.assertEqual(result, expected)
