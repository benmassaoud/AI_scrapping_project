import sqlite3


class Database:

    def __init__(self, db_name):
        self.db_name = db_name
        self._db_connection = sqlite3.connect(self.db_name, isolation_level=None)
        self.db_cur = self._db_connection.cursor()

    def query(self, query, params):
        return self.db_cur.execute(query, params)

    def query_many(self, query, params):
        return self.db_cur.executemany(query, params)

    def __del__(self):
        self._db_connection.close()
