# encoding: utf-8

import os
import subprocess
import sys
from itertools import chain, islice

from colors import green, red
from six import u


def paginate_external(data):
    """Executes the external pager ($PAGER). Waits until the pager
    exits. Writes out an error message to ``sys.stderr`` if an
    ``OSError`` is raised during the operation.
    """
    command = os.environ.get('PAGER', 'less').split()
    try:
        pager = subprocess.Popen(command, stdin=subprocess.PIPE)
        pager.communicate(data)
    except OSError as e:
        msg = "Error executing pager: {0}\n".format(e)
        sys.stderr.write(red(msg))

def _get_key(console):
    console.prepare()
    try:
        for event in iter(console.get_event, None):
            if event.evt == "key":
                return event.data
    finally:
        console.restore()

def paginate(console, lines):
    already_printed_lines = []
    while True:
        height = console.height - 1
        for (i, line) in enumerate(islice(lines, height), 1):
            already_printed_lines.append(line)
            sys.stdout.write(line)
            sys.stdout.write("\n")
        if i < height:
            break
        msg = "Press '<space>' for next page or 'p' to open pager"
        sys.stdout.write(green(msg))
        sys.stdout.flush()
        key = _get_key(console)
        sys.stdout.write("\r" + " " * len(msg) + "\r")
        sys.stdout.flush()
        if key == u(" "):
            continue
        elif key == u("p"):
            lines = chain(already_printed_lines, lines)
            paginate_external(("\n").join(lines).encode(console.encoding))
        break
