# encoding: utf-8

from __future__ import unicode_literals

import textwrap
import unittest

from eekhoorn.table import DefaultCellRenderer, Table


class TableTest(unittest.TestCase):
    def test_empty_table(self):
        expected = textwrap.dedent("""\
            ╒╕
            ╞╡
            └┘""")
        table = "\n".join(Table([]).render())
        self.assertEqual(table, expected)

    def test_only_header_with_single_column(self):
        expected = textwrap.dedent("""\
            ╒══════╕
            │ spam │
            ╞══════╡
            └──────┘""")
        renderer = DefaultCellRenderer("center")
        table = "\n".join(Table([("spam", renderer)]).render())
        self.assertEqual(table, expected)

    def test_only_header_with_columns(self):
        expected = textwrap.dedent("""\
            ╒══════╤══════╕
            │ spam │ eggs │
            ╞══════╪══════╡
            └──────┴──────┘""")
        renderer = DefaultCellRenderer("left")
        table = Table([("spam", renderer), ("eggs", renderer)], 15)
        lines = list(table.render())
        for line in lines:
            self.assertEqual(len(line), 15)
        self.assertEqual("\n".join(lines), expected)

    def test_full_table(self):
        expected = textwrap.dedent("""\
            ╒══════════════════╤═══════════╕
            │     Column A     │  Column B │
            ╞══════════════════╪═══════════╡
            │ Value 1 A        │ Value 1 B │
            ├──────────────────┼───────────┤
            │ Value 2 A longer │       2 B │
            └──────────────────┴───────────┘""")
        left_renderer = DefaultCellRenderer("left")
        right_renderer = DefaultCellRenderer("right")
        table = Table([
            ("Column A", left_renderer),
            ("Column B", right_renderer)
        ])
        table.add_row(["Value 1 A", "Value 1 B"])
        table.add_row(["Value 2 A longer", "2 B"])
        rendered_table = "\n".join(table.render())
        self.assertEqual(rendered_table, expected)


class RowTest(unittest.TestCase):
    def test_left_justify(self):
        expected = "| spam    |"
        table = Table([("fooobar", None)])
        renderer = DefaultCellRenderer("left")
        lines = table.render_row([("spam", renderer)], "|", "|", "+")
        self.assertEqual(next(lines), expected)

    def test_left_justify_multiple_columns(self):
        expected = "| spam    + eggs   |"
        table = Table([("fooobar", None), ("raboof", None)])
        renderer = DefaultCellRenderer("left")
        lines = table.render_row(
            [("spam", renderer), ("eggs", renderer)], "|", "|", "+")
        self.assertEqual(next(lines), expected)


class SepLineTest(unittest.TestCase):
    def test_empty(self):
        expected = "||"
        table = Table([])
        line = table._render_sep_line("|", "|", "-", "+")
        self.assertEqual(line, expected)

    def test_multiple(self):
        expected = "|---+---|"
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
