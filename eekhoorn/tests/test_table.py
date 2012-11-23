# encoding: utf-8

import textwrap
import unittest

from six import u

from eekhoorn.table import DefaultCellRenderer, Table


class TableTest(unittest.TestCase):
    def test_empty_table(self):
        expected = textwrap.dedent(u("""\
            \u2552\u2555
            \u255e\u2561
            \u2514\u2518"""))
        table = u("\n").join(Table([]).render())
        self.assertEqual(table, expected)

    def test_only_header_with_single_column(self):
        expected = textwrap.dedent(u("""\
            \u2552\u2550\u2550\u2550\u2550\u2550\u2550\u2555
            \u2502 spam \u2502
            \u255e\u2550\u2550\u2550\u2550\u2550\u2550\u2561
            \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2518"""))
        renderer = DefaultCellRenderer("center")
        table = u("\n").join(Table([("spam", renderer)]).render())
        self.assertEqual(table, expected)

    def test_only_header_with_columns(self):
        expected = textwrap.dedent(u("""\
            \u2552\u2550\u2550\u2550\u2550\u2550\u2550\u2564\u2550\u2550\u2550\u2550\u2550\u2550\u2555
            \u2502 spam \u2502 eggs \u2502
            \u255e\u2550\u2550\u2550\u2550\u2550\u2550\u256a\u2550\u2550\u2550\u2550\u2550\u2550\u2561
            \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2518"""))
        renderer = DefaultCellRenderer("left")
        table = Table([("spam", renderer), ("eggs", renderer)], 15)
        lines = list(table.render())
        for line in lines:
            self.assertEqual(len(line), 15)
        self.assertEqual(u("\n").join(lines), expected)

    def test_full_table(self):
        expected = textwrap.dedent(u("""\
            \u2552\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2564\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2555
            \u2502     Column A     \u2502  Column B \u2502
            \u255e\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u256a\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2550\u2561
            \u2502 Value 1 A        \u2502 Value 1 B \u2502
            \u251c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u253c\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2524
            \u2502 Value 2 A longer \u2502       2 B \u2502
            \u2514\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2534\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2500\u2518"""))
        left_renderer = DefaultCellRenderer("left")
        right_renderer = DefaultCellRenderer("right")
        table = Table([
            ("Column A", left_renderer),
            ("Column B", right_renderer)
        ])
        table.add_row(["Value 1 A", "Value 1 B"])
        table.add_row(["Value 2 A longer", "2 B"])
        rendered_table = u("\n").join(table.render())
        self.assertEqual(rendered_table, expected)


class RowTest(unittest.TestCase):
    def test_left_justify(self):
        expected = u("| spam    |")
        table = Table([("fooobar", None)])
        renderer = DefaultCellRenderer("left")
        lines = table.render_row([("spam", renderer)], "|", "|", "+")
        self.assertEqual(next(lines), expected)

    def test_left_justify_multiple_columns(self):
        expected = u("| spam    + eggs   |")
        table = Table([("fooobar", None), ("raboof", None)])
        renderer = DefaultCellRenderer("left")
        lines = table.render_row(
            [("spam", renderer), ("eggs", renderer)], "|", "|", "+")
        self.assertEqual(next(lines), expected)


class SepLineTest(unittest.TestCase):
    def test_empty(self):
        expected = u("||")
        table = Table([])
        line = table._render_sep_line("|", "|", "-", "+")
        self.assertEqual(line, expected)

    def test_multiple(self):
        expected = u("|---+---|")
        table = Table([("a", None), ("b", None)])
        line = table._render_sep_line("|", "|", "-", "+")
        self.assertEqual(line, expected)


class MaxWidthtest(unittest.TestCase):
    def test_wrapping(self):
        renderer = DefaultCellRenderer("left")
        table = Table([("spam", renderer), ("eggs", renderer)], 25)
        table.add_row(["spam " * 10, "eggs " * 5])
        for line in table.render():
            self.assertEqual(len(line), 25)

class DefaultCellRendererTest(unittest.TestCase):
    def test_render_empty_value(self):
        width = 5
        expected = [" " * width]
        renderer = DefaultCellRenderer("left")
        lines = list(renderer.render("", width))
        self.assertEqual(lines, expected)
