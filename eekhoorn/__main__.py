# encoding: utf-8

import argparse
import sys
from contextlib import closing
from functools import partial
from itertools import islice

import sqlalchemy.exc
from colors import green, red
from pyrepl.unix_console import UnixConsole
from six import integer_types, u

from eekhoorn.gateway import DatabaseGateway
from eekhoorn.reader import Reader
from eekhoorn.table import DefaultCellRenderer, Table


ENCODING = "utf-8"


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
            value = u("NULL")
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
    for row in islice(result, 10):
        table.add_row(row)
    return u("\n").join(table.render())

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
                sys.stdout.write(tableify(result, console.width))
                sys.stdout.write("\n")
        msg = "Query took {0:.4f} seconds\n".format(gateway.last_query_time)
        sys.stdout.write(msg)


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    parser = argparse.ArgumentParser()
    parser.add_argument("url")
    args = parser.parse_args(args)

    gateway = DatabaseGateway(args.url)
    console = UnixConsole(encoding=ENCODING)
    reader = Reader(console)
    sys.stdout.write(", ".join(gateway.tables))
    sys.stdout.write("\n")
    sys.stdout.write("Welcome to eekhoorn, the fancy SQL console.\n")
    while True:
        try:
            line = reader.readline(True)
        except EOFError:
            break
        else:
            do_query(console, gateway, line)

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
