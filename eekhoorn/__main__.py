# encoding: utf-8

from __future__ import unicode_literals

import argparse
import io
import os
import sys
from contextlib import closing
from functools import partial
from itertools import islice

import sqlalchemy.exc
from colors import green, red
from pyrepl.unix_console import UnixConsole
from six import integer_types

from eekhoorn.gateway import DatabaseGateway
from eekhoorn.reader import Reader
from eekhoorn.pager import paginate
from eekhoorn.table import DefaultCellRenderer, Table


ENCODING = "utf-8"
MAX_ROWS = 250
HISTORY_PATH = "~/.eekhoornhistory"


class CellRenderer(object):
    def __init__(self):
        self.renderer_left = DefaultCellRenderer("left")
        self.renderer_right = DefaultCellRenderer("right")

    def estimate_width(self, value):
        return self.renderer_left.estimate_width(value)

    def render(self, value, width):
        color = None
        renderer = self.renderer_left
        if value is None:
            value = "NULL"
            color = partial(red, style="italic")
            renderer = self.renderer_right
        elif isinstance(value, integer_types + (float, )):
            color = green
            renderer = self.renderer_right
        for line in renderer.render(value, width):
            if color is not None:
                line = color(line)
            yield line

def tableify(result, max_width):
    renderer = CellRenderer()
    columns = zip(result.keys(), [renderer] * len(result.keys()))
    table = Table(columns, max_width=max_width)
    for row in islice(result, MAX_ROWS):
        table.add_row(row)
    return table.render()

def do_query(console, gateway, source):
    "Executes the query and formats the result."
    try:
        result = gateway.execute(source)
    except sqlalchemy.exc.SQLAlchemyError as exc:
        sys.stderr.write(red(str(exc)))
        sys.stderr.write("\n")
    else:
        with closing(result):
            if result.returns_rows:
                lines = tableify(result, console.width)
                paginate(console, lines)
        msg = "Query took {0:.4f} seconds".format(gateway.last_query_time)
        sys.stdout.write(msg)

        if result.supports_sane_rowcount() and result.rowcount > -1:
            sys.stdout.write(" ({0:n} rows)".format(result.rowcount))

        sys.stdout.write("\n")



def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args(args)

    gateway = DatabaseGateway(args.url)
    console = UnixConsole(encoding=ENCODING)
    reader = Reader(console=console, gateway=gateway)
    history_path = os.path.expanduser(HISTORY_PATH)
    try:
        with io.open(history_path, "r", encoding="utf-8") as hist_file:
            for line in hist_file:
                reader.history.append(line.strip())
    except EnvironmentError:
        pass
    sys.stdout.write("Welcome to eekhoorn, the fancy SQL console.\n")
    while True:
        try:
            line = reader.readline(True)
        except EOFError:
            break
        else:
            do_query(console, gateway, line)
    with io.open(history_path, "w", encoding="utf-8") as hist_file:
        for line in reader.history:
            hist_file.write(line + "\n")

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
