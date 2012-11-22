# encoding: utf-8

import time

import sqlalchemy
from sqlalchemy import event


class DatabaseGateway(object):
    """Gateway for talking to the database.
    """

    def __init__(self, url):
        self.engine = sqlalchemy.create_engine(url)
        #: Time that the last query took or `None`.
        self.last_query_time = None
        self.metadata = sqlalchemy.MetaData()
        self.metadata.bind = self.engine
        self.metadata.reflect()
        event.listen(
            self.engine, "before_cursor_execute", self._on_before_execute)
        event.listen(
            self.engine, "after_cursor_execute", self._on_after_execute)

    def _on_before_execute(self, conn, cursor, statement, parameters,
                           context, executemany):
        context._query_start_time = time.time()

    def _on_after_execute(self, conn, cursor, statement, parameters,
                          context, executemany):
        self.last_query_time = time.time() - context._query_start_time

    @property
    def tables(self):
        "Returns the name of the tables that exist in the current database."
        return self.metadata.tables

    def execute(self, query):
        return self.engine.execute(query)
