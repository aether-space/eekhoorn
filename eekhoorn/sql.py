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
        retval.extend(sql.Token(Token.Error.Next, t.value) for t in tokens)
        return retval
    return [sql.Token(Token.Text, u(""))]

def flatten(tokens):
    """Given an iterable of tokens, returns an iterable with flattened
    tokens.
    """
    return chain.from_iterable(token.flatten() for token in tokens)

def _skip_ws(tokens_iter):
    "Returns the next token that is not whitespace."
    for token in tokens_iter:
        if token.value.strip(u("\n\r\t\v ")):
            return token
    return None

def statement_finished(source):
    """Returns whether the given source contains a finished (i.e. ending
    with a ':') SQL statement."""
    token_iter = reversed(list(flatten(get_tokens(source))))
    for token in token_iter:
        if token.ttype == Token.Punctuation and token.value == u(";"):
            # Seems like the statement is finished, but there is still
            # the possibility that the previous tokens is an error
            # token, which means the statement is still incomplete
            # (e.g. an opened string literal)
            previous_token = _skip_ws(token_iter)
            return previous_token and previous_token.ttype != Token.Error
        elif token.ttype == Token.Error.Next:
            return True
        elif token.ttype not in _whitespace:
            break
    return False
