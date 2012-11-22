# encoding: utf-8

from colors import red
from pyrepl import commands, completing_reader
from pyrepl.historical_reader import HistoricalReader
from six import u

from eekhoorn import highlighting_reader
from eekhoorn.sql import statement_finished


class maybe_accept(commands.Command):
    def do(self):
        self.finish = statement_finished(self.reader.get_unicode())
        if not self.finish:
            self.reader.insert(u("\n"))

class complete(completing_reader.complete):
    def do(self):
        reader = self.reader
        line = reader.buffer[reader.bol():reader.eol()]
        if all((c in ["\t", " "]) for c in line):
            reader.insert("\t")
        else:
            return super(complete, self).do()

class Reader(
        HistoricalReader,
        completing_reader.CompletingReader,
        highlighting_reader.HighlightingReader
):
    # Don't show completion suggestions inside "[]"
    use_brackets = False

    def __init__(self, console):
        super(Reader, self).__init__(console)
        self.ps1 = "sql> "
        self.ps2 = "sql> "
        self.ps3 = "  -> "
        self.ps4 = "  -> "
        self.commands["complete"] = complete
        self.commands["maybe-accept"] = maybe_accept
        self._add_keybindings()

    def _add_keybindings(self):
        """This is a hack, but pyrepl's keymap stuff seems to be
        broken. Ideally, all those should just be other items in
        `collect_keymap`.
        """
        # M-b
        self.input_trans.ck["\x1bb"] = u("backward-word")
        # C-left
        self.input_trans.ck["\x1b[D"] = u("backward-word")
        # M-f
        self.input_trans.ck["\x1bf"] = u("forward-word")
        # C-right
        self.input_trans.ck["\x1b[C"] = u("forward-word")

    def collect_keymap(self):
        keymap = super(Reader, self).collect_keymap()
        return keymap + (
            (r'\n', 'maybe-accept'),
            # XXX not working yet
            (r'\M-b', 'backward-word'),
            (r"\M-f", "forward-word"),
        )

    def error(self, msg):
        "More pretty error messages."
        self.msg = red(msg)
        self.dirty = True
