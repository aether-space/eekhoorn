# encoding: utf-8

try:
    import unittest2 as unittest
except ImportError:
    import unittest

import sqlparse
from pyrepl.reader import make_default_syntax_table
from six import u

from eekhoorn.completion import (
    get_all_identifiers,get_completions, get_current_token)


class TestReader(object):
    def __init__(self, input, pos = None):
        self.buffer = list(input)
        if pos is None:
            self.pos = len(input)
        else:
            self.pos = pos
        self.syntax_table = make_default_syntax_table()

    def get_unicode(self):
        return u("").join(self.buffer)

class TestGateway(object):
    def __init__(self, tables):
        self.tables = tables

class TestTable(object):
    def __init__(self, columns):
        self.columns = [TestColumn(name) for name in columns]

class TestColumn(object):
    def __init__(self, name):
        self.name = name


class GetAllIdentifiersTest(unittest.TestCase):
    def assertEqualIdents(self, source, expected_idents):
        tokens = sqlparse.parse(source)[0].tokens
        idents = dict(get_all_identifiers(tokens))
        self.assertEqual(idents, expected_idents)

    def test_no_identifiers(self):
        self.assertEqualIdents("SELECT 42", {})

    def test_no_alias(self):
        self.assertEqualIdents(
            "SELECT * FROM spam",
            {u("spam"): set([u("spam")])})

    def test_alias(self):
        self.assertEqualIdents(
            "SELECT * FROM spam sp",
            {u("sp"): set([u("spam")])})

    def test_multiple_aliases(self):
        self.assertEqualIdents(
            "SELECT sp.id FROM spam sp, eggs e",
            {u("id"): set([u("spam.id")]),
             u("sp"): set([u("spam")]),
             u("e"): set([u("eggs")])})


class GetCurrentToken(unittest.TestCase):
    def test_aliased_where(self):
        source = u("SELECT * FROM spam sp WHERE sp.")
        tokens = sqlparse.parse(source)[0].tokens
        token = get_current_token(tokens, len(source))
        self.assertIsNotNone(token)


class CompletionsTest(unittest.TestCase):
    def assertCompletionsEqual(self, input, stem, tables, expected_completions):
        reader = TestReader(input)
        gateway = TestGateway(tables)
        completions = get_completions(reader, stem, gateway)
        self.assertEqual(completions, expected_completions)

    def test_keyword(self):
        self.assertCompletionsEqual(u("SELEC"), u("SELEC"), {}, [u("SELECT")])

    def test_columns_no_matching_table(self):
        self.assertCompletionsEqual(u("SELECT sp."), u(""),  {}, [])

    def test_matching_table(self):
        self.assertCompletionsEqual(
            u("SELECT * FROM example_"),
            u("example_"),
            {u("example_table"): None},
            [u("example_table")])

    def test_matching_columns(self):
        columns = [u("id"), u("spam"), u("eggs")]
        self.assertCompletionsEqual(
            u("SELECT * FROM example_table et WHERE et."),
            u(""),
            {u("example_table"): TestTable(columns)},
            sorted(columns))

    def test_unique_columns_match(self):
        columns_spam = [u("id"), u("spam")]
        columns_eggs = [u("id"), u("eggs")]
        reader = TestReader(u("SELECT  FROM spam, eggs"), pos=len(u("SELECT ")))
        gateway = TestGateway({
            u("spam"): TestTable(columns_spam),
            u("eggs"): TestTable(columns_eggs)
        })
        completions = get_completions(reader, u(""), gateway)
        self.assertNotIn(u("id"), completions)
        self.assertIn(u("spam"), completions)
        self.assertIn(u("eggs"), completions)
