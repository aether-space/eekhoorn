# encoding: utf-8

import sys

from pyrepl.unix_console import UnixConsole

from eekhoorn.reader import Reader


def main(args=None):
    if args is None:
        args = sys.argv[1:]

    console = UnixConsole(encoding="utf-8")
    reader = Reader(console)
    while True:
        try:
            line = reader.readline(True)
        except EOFError:
            break
        else:
            print(repr(line))

    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
