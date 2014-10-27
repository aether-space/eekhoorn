# encoding: utf-8

from __future__ import unicode_literals

from collections import deque
from itertools import chain

import pyrepl.reader
from colors import color
from six.moves import xrange
from sqlparse import sql
from sqlparse.tokens import Token

from eekhoorn.sql import get_tokens, flatten


_disp_str = pyrepl.reader.disp_str

STYLE = {
    None: ("", ""),
    Token: ("", ""),
    Token.Comment: (42, "italic"),
    Token.Keyword: (23, "bold"),
    Token.Error: ("red", "")
}

def format_token(token):
    "Formats a single token."
    ttype = token.ttype
    while ttype is not None and ttype not in STYLE and ttype.parent is not None:
        ttype = ttype.parent
    (fg, style) = STYLE[ttype]
    formatted = color(token.value, fg=fg, style=style)
    return formatted

def group_by_line(tokens):
    "Flattens tokens and groups them by line."
    tokens = deque(flatten(tokens))
    line = []
    while tokens:
        token = tokens.popleft()
        if "\n" not in token.value:
            line.append(token)
        else:
            (value, _, rest) = token.value.partition("\n")
            tokens.appendleft(sql.Token(token.ttype, rest))
            line.append(sql.Token(token.ttype, value))
            yield line
            line = []

    if line:
        yield line

def _add_line_part(
        screen, screeninfo, tokens, pos, width=-1, prefix="", suffix=""):
    """
    Returns an iterable of remaining tokens.
    """
    l = ""
    l2 = []
    total_length = 0
    leftovers = []
    tokens_iter = iter(tokens)
    for token in tokens_iter:
        chars_left = width - total_length
        value_length = len(token.value)
        if width >= 0 and chars_left < value_length:
            leftovers.append(sql.Token(token.ttype, token.value[chars_left:]))
            token.value = token.value[:chars_left]
        total_length += value_length
        (part, part_info) = _disp_str(token.value)
        token.value = part
        l += format_token(token)
        l2.extend(part_info)
        if leftovers:
            break
    if width < 0:
        l2.append(1)
    screen.append(prefix + l + suffix)
    screeninfo.append((pos, l2))
    return chain(leftovers, tokens_iter)


class HighlightingReader(pyrepl.reader.Reader):
    """A reader that highlights SQL using ANSI escape sequences.
    """

    wrap_sign = "\N{LEFTWARDS ARROW WITH HOOK}"

    def calc_screen(self):
        # c/p from pyrepl.reader.Reader with added highlighting
        # XXX This is a mess
        def add(*args, **kwargs):
            remaining_tokens = _add_line_part(
                screen, screeninfo, tokens, *args, **kwargs)
            # Unfortunately, pyrepl's UnixConsole asumes it can get
            # the length (on screen) of the new line using len(), to
            # check whether the new line completely overwrites the old
            # line. Due to escape sequences, that doesn't work at all,
            # hence always explicitly clear to the end of line
            screen[-1] += self.console._el
            return remaining_tokens
        screen = []
        screeninfo = []
        input = self.get_unicode()
        tokens = get_tokens(input)
        # One char left for the wrap sign
        w = self.console.width - 1
        pos = self.pos
        for (lineno, tokens) in enumerate(group_by_line(tokens)):
            line = "".join(t.value for t in tokens)
            line_length = len(line)
            if 0 <= pos <= line_length:
                if self.msg and not self.msg_at_bottom:
                    for mline in self.msg.split("\n"):
                        screen.append(mline)
                        screeninfo.append((0, []))
                self.lxy = pos, lineno
            prompt = self.get_prompt(lineno, line_length >= pos >= 0)
            while '\n' in prompt:
                pre_prompt, _, prompt = prompt.partition('\n')
                screen.append(pre_prompt)
                screeninfo.append((0, []))
            pos -= line_length + 1
            prompt, linepos = self.process_prompt(prompt)
            l = _disp_str(line)[0]
            wrapcount = (len(l) + linepos) // w
            if wrapcount == 0:
                add(linepos, prefix=prompt)
            else:
                tokens = add(linepos, w - linepos, prompt, self.wrap_sign)
                for _ in xrange(wrapcount - 1):
                    tokens = add(0, w, suffix=self.wrap_sign)
                add(0)
        self.screeninfo = screeninfo
        self.cxy = self.pos2xy(self.pos)
        if self.msg and self.msg_at_bottom:
            for mline in self.msg.split("\n"):
                screen.append(mline)
                screeninfo.append((0, []))
        return screen
