# encoding: utf-8

from itertools import chain

import sqlparse
from six import u
from sqlparse import sql
from sqlparse.tokens import Token


_whitespace = set([Token.Text, Token.Text.Whitespace])

def get_tokens(source):
    """Returns a list of all tokens, not separated by statement. All
    tokens not belonging to the first statement are returned as error
    tokens.
    """
    stmts = sqlparse.parse(source)
    if stmts:
        retval = stmts[0].tokens
        tokens = chain.from_iterable(stmt.tokens for stmt in stmts[1:])
        retval.extend(sql.Token(Token.Error, t.value) for t in tokens)
        return retval
    return [sql.Token(Token.Text, u(""))]

def statement_finished(source):
    """Returns whether the given source contains a finished (i.e. ending
    with a ':') SQL statement."""
    for token in reversed(get_tokens(source)):
        if token.ttype == Token.Punctuation and token.value == u(";"):
            return True
        elif token.ttype == Token.Error:
            return True
        elif token.ttype not in _whitespace:
            break
    return False
