# encoding: utf-8

import unittest

from eekhoorn.sql import statement_finished


class SqlTest(unittest.TestCase):
    def test_finished(self):
        sql = "SELECT * FROM spam WHERE eggs LIKE '%';"
        self.assertTrue(statement_finished(sql))

    def test_unfinished_string(self):
        sql = "SELECT ';"
        self.assertFalse(statement_finished(sql))

    def test_unfinished_string_with_newline(self):
        sql = "SELECT '\n;"
        self.assertFalse(statement_finished(sql))

    @unittest.skip("Bug in sqlparse")
    def test_unfinished(self):
        sql = "SELECT '\n;\n'"
        self.assertFalse(statement_finished(sql))

    def test_finished_multiline_string(self):
        sql = "SELECT '\n;\n';"
        self.assertTrue(statement_finished(sql))
