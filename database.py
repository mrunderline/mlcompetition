from sqlite3 import connect
from setting import *


class Database:
    instance = None
    competition_cols = ['id', 'title', 'evaluator', 'evaluation_file_path', 'created_at']
    leader_board_cols = ['id', 'competition_id', 'name', 'score', 'created_at']

    # def __new__(cls, *args, **kwargs):
    #     if cls.instance is None:
    #         cls.instance = super().__new__(cls)
    #         cls.instance.is_initialized = False
    #     return cls.instance

    def __init__(self):
        # if self.is_initialized:
        #     return

        self.conn = connect(DB_URL)
        self.cur = self.conn.cursor()
        self.is_initialized = True

    def query(self, query):
        # print(query)
        self.cur.execute(query)

    def fetchall(self):
        return self.cur.fetchall()

    def fetchone(self):
        return self.cur.fetchone()

    def commit(self):
        self.conn.commit()

    def rollback(self):
        self.conn.rollback()

    def close(self):
        self.cur.close()
        self.conn.close()
        self.instance = None
        self.is_initialized = False


def pre_define_db():
    db = Database()

    # create competition table
    db.query("""
        create table if not exists competitions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            evaluator TEXT,
            evaluation_file_path TEXT,
            created_at DATE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    # create leader board table
    db.query("""
        create table if not exists leader_board(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            competition_id INTEGER,
            name TEXT,
            score REAL,
            created_at DATE DEFAULT CURRENT_TIMESTAMP
        );
    """)

    db.commit()
    db.close()
