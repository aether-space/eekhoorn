# encoding: utf-8

from collections import defaultdict, deque
from functools import partial

import sqlparse
from pyrepl import completing_reader
from six import iteritems, itervalues, next, text_type, u
from sqlparse.keywords import KEYWORDS_COMMON
from sqlparse.sql import Identifier


def get_all_identifiers(tokens):
    "Returns all identifiers as mapping aliased name => set of real names."
    idents = defaultdict(set)
    maybe_expand = defaultdict(set)
    tokens = deque(tokens)
    while tokens:
        token = tokens.popleft()
        if isinstance(token, Identifier):
            parent_name = token.get_parent_name()
            real_name = token.get_real_name()
            if parent_name:
                name = token.get_name()
                if name is not None:
                    # Parent's name might be an alias
                    maybe_expand[name].add((parent_name, real_name))
            else:
                idents[token.get_name()].add(real_name)
        elif token.is_group():
            tokens.extendleft(token.tokens)
    for (alias, values) in iteritems(maybe_expand):
        for (parent_name, name) in values:
            expansions = idents.get(parent_name)
            if expansions and len(expansions) == 1:
                parent_name = next(iter(expansions))
            idents[alias].add(u("{0}.{1}").format(parent_name, name))
    return idents

def find_identifier(tokens, name):
    """Given the tokens of a statement and a possibly aliased name, return
    the unaliased name or `None`.
    """
    real_names = get_all_identifiers(tokens).get(name)
    if real_names is not None:
        return next(iter(real_names))
    return None

def get_current_token(tokens, pos):
    token_pos = 0
    for token in tokens:
        token_pos += len(text_type(token))
        if token_pos >= pos:
            return token
    return None


def get_unique_column_names(used_idents, tables):
    #: Mapping column name => table name. Table name is `None` if the
    # column is found in more than one table
    columns = {}
    for real_names in itervalues(used_idents):
        for table_name in real_names:
            if not u(".") in table_name:
                table = tables.get(table_name)
                if table is not None:
                    for column in table.columns:
                        if column.name not in columns:
                            columns[column.name] = table_name
                        elif columns[column.name] != table_name:
                            columns[column.name] = None
    for (column_name, table_name) in iteritems(columns):
        if table_name is not None:
            yield column_name


def get_completions(reader, stem, gateway):
    "Returns a list of possible completions."
    def extend(iterable):
        """Extends the set of suggestions with items from `iterable`. Filters
        non-matching items.
        """
        suggestions.update(
            item for item in iterable if item.startswith(stem))
    suggestions = set()
    tables = gateway.tables
    stmt = sqlparse.parse(reader.get_unicode())[0]
    idents = get_all_identifiers(stmt.tokens)
    token = get_current_token(stmt.flatten(), reader.pos)
    if token and isinstance(token.parent, Identifier):
        token = token.parent
    add_all = True
    if isinstance(token, Identifier):
        parent_name = token.get_parent_name()
        if parent_name:
            add_all = False
            if parent_name in idents:
                parent_name = next(iter(idents.get(parent_name)))
            table = tables.get(parent_name)
            if table is not None:
                extend(column.name for column in table.columns)
    if add_all:
        extend(KEYWORDS_COMMON)
        extend(tables)
        extend(idents)
        extend(get_unique_column_names(idents, tables))
        if stem in suggestions:
            # No real point in suggesting the same thing that is
            # already entered and it can lead to false results as
            # sqlparse might recognize unfinished keywords as
            # identifiers
            suggestions.remove(stem)
    return sorted(suggestions)


class CompletingReader(completing_reader.CompletingReader):
    # Don't show completion suggestions inside "[]"
    use_brackets = False

    def __init__(self, gateway, **kwargs):
        super(CompletingReader, self).__init__(**kwargs)
        self.get_completions = partial(get_completions, self, gateway=gateway)
