# encoding: utf-8

"""
    Fancy Unicode tables.
"""

from collections import defaultdict
from textwrap import wrap

from six import text_type, u
from six.moves import xrange


class DefaultCellRenderer(object):
    "The default cell renderer."

    JUSTIFIERS = {
        "left": lambda s, w: (u(" ") + s).ljust(w),
        "right": lambda s, w: (s + u(" ")).rjust(w),
        "center": lambda s, w: s.center(w)
    }

    wrap_sign = u("\N{LEFTWARDS ARROW WITH HOOK}")

    def __init__(self, justification="left"):
        if justification not in self.JUSTIFIERS:
            msg = "Unknown justification: {0!r}"
            raise ValueError(msg.format(justification))
        self.justifier = self.JUSTIFIERS[justification]

    def estimate_width(self, value):
        # 2 ^= Spaces to the left and right
        return len(text_type(value)) + 2

    def render(self, value, width):
        lines = wrap(text_type(value), width - 2)
        if not lines:
            lines = [""]
        for (i, line) in enumerate(lines):
            line = self.justifier(line, width)
            if i < (len(lines) - 1):
                # Replace last space with a wrap sign
                line = line[:-1] + self.wrap_sign
            yield line


class Table(object):
    """Renders beautiful text tables.

    Example usage::

       >>> table = Table()
       >>> renderer_left = DefaultCellRenderer("left")
       >>> renderer_right = DefaultCellRenderer("right")
       >>> table = Table([
       ...     ("Column 1", renderer_left),
       ...     ("Column 2", renderer_right)
       ... ])
       >>> table.add_row(["row 1", "row 1 other second column"])
       >>> table.add_row(["another row", "another second value"])
       >>> print("\n".join(table.render()))
       ╒═════════════╤═══════════════════════════╕
       │   Column 1  │          Column 2         │
       ╞═════════════╪═══════════════════════════╡
       │ row 1       │ row 1 other second column │
       ├─────────────┼───────────────────────────┤
       │ another row │      another second value │
       └─────────────┴───────────────────────────┘
    """

    (LEFT, RIGHT, MIDDLE, SEP) = xrange(4)

    # Chars used for the first line in header
    header_top = [
        u("\N{BOX DRAWINGS DOWN SINGLE AND RIGHT DOUBLE}"),
        u("\N{BOX DRAWINGS DOWN SINGLE AND LEFT DOUBLE}"),
        u("\N{BOX DRAWINGS DOUBLE HORIZONTAL}"),
        u("\N{BOX DRAWINGS DOWN SINGLE AND HORIZONTAL DOUBLE}")
    ]

    # Chars used for the middle line in header
    header_middle = [
        u("\N{BOX DRAWINGS LIGHT VERTICAL}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL}")
    ]

    # Chars used for the last line in header
    header_bottom = [
        u("\N{BOX DRAWINGS VERTICAL SINGLE AND RIGHT DOUBLE}"),
        u("\N{BOX DRAWINGS VERTICAL SINGLE AND LEFT DOUBLE}"),
        u("\N{BOX DRAWINGS DOUBLE HORIZONTAL}"),
        u("\N{BOX DRAWINGS VERTICAL SINGLE AND HORIZONTAL DOUBLE}")
    ]

    # Chars used for the table's last line
    bottom = [
        u("\N{BOX DRAWINGS LIGHT UP AND RIGHT}"),
        u("\N{BOX DRAWINGS LIGHT UP AND LEFT}"),
        u("\N{BOX DRAWINGS LIGHT HORIZONTAL}"),
        u("\N{BOX DRAWINGS LIGHT UP AND HORIZONTAL}")
    ]

    row = [
        u("\N{BOX DRAWINGS LIGHT VERTICAL}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL}")
    ]

    line = [
        u("\N{BOX DRAWINGS LIGHT VERTICAL AND RIGHT}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL AND LEFT}"),
        u("\N{BOX DRAWINGS LIGHT HORIZONTAL}"),
        u("\N{BOX DRAWINGS LIGHT VERTICAL AND HORIZONTAL}")
    ]

    def __init__(self, columns, max_width=None):
        self.columns = []
        self.renderers = []
        self.max_width = max_width
        self._widths = {}
        for (name, renderer) in columns:
            if renderer is None:
                renderer = DefaultCellRenderer()
            self.add_column(name, renderer)
            self._widths[name] = len(name) + 2
        self.row_data = []

    def add_column(self, name, renderer):
        """Adds a new column `name` to the table that formats its values using
        the given cell renderer.
        """
        self.columns.append(name)
        self.renderers.append(renderer)

    def add_row(self, row_data):
        """Adds a single row to the table. `row_data` should be an iterable
        with `six.text_type` values.
        """
        row = []
        for (i, (name, value)) in enumerate(zip(self.columns, row_data)):
            # 2 == one space in front and behind
            width = self.renderers[i].estimate_width(value)
            if width > self._widths[name]:
                self._widths[name] = width
            row.append(value)
        self.row_data.append(row)

    def recalc_column_widths(self):
        """Shrink columns so that the complete table is smaller than
        `max_width`.
        """
        # max_width - left and right - column separators
        max_width = self.max_width - 2 - max(0, len(self.columns) - 1)
        max_column_width = max_width / len(self.columns)
        columns_to_divide = []
        space_taken = 0
        for (name, width) in self._widths.items():
            if width > max_column_width:
                columns_to_divide.append(name)
            else:
                space_taken += width
        (space_for_each, space_left) = divmod(
            max_width - space_taken, len(columns_to_divide))
        for name in columns_to_divide:
            self._widths[name] = space_for_each
        self._widths[name] += space_left

    @property
    def width(self):
        "The table's current width (might change if more rows are added)"
        # Assumes all the left and right table decorations as well as
        # the column separators are only one char wide
        return sum(self._widths.values()) + 2 + max(0, len(self.columns) - 1)

    def render(self):
        "Returns an iterable of lines."
        if self.max_width and self.width > self.max_width:
            self.recalc_column_widths()
        for line in self.render_header():
            yield line
        for (i, row) in enumerate(self.row_data):
            if i > 0:
                yield self._render_sep_line(*self.line)
            lines = self.render_row(zip(row, self.renderers), *self.row)
            for line in lines:
                yield line
        yield self.render_bottom()

    def render_header(self):
        yield self._render_sep_line(*self.header_top)
        cell_renderer = DefaultCellRenderer("center")
        cell_renderer.wrap_sign = " "
        header_row = zip(self.columns, [cell_renderer] * len(self.columns))
        lines = self.render_row(header_row, *self.header_middle)
        for line in lines:
            yield line
        yield self._render_sep_line(*self.header_bottom)

    def render_bottom(self):
        return self._render_sep_line(*self.bottom)

    def _render_sep_line(self, left, right, middle, sep):
        "Draws a separation line using the given symbols."
        return u("").join([
            left,
            sep.join(middle * self._widths[name] for name in self.columns),
            right])

    def render_row(self, row, left, right, sep):
        # XXX this became a bit messy
        justified_lines = defaultdict(list)
        number_of_lines = []
        iterable = enumerate(zip(self.columns, row))
        for (x, (name, (value, renderer))) in iterable:
            width = self._widths[name]
            for (y, line) in enumerate(renderer.render(value, width)):
                justified_lines[(x, y)] = line
            number_of_lines.append(y + 1)
        if not justified_lines:
            return
        for y in xrange(max(number_of_lines)):
            values = []
            for x in xrange(len(self.columns)):
                value = justified_lines.get((x, y))
                if value is None:
                    value = u(" ") * self._widths[self.columns[x]]
                values.append(value)
            yield u("").join([
                left,
                sep.join(values),
                right])
