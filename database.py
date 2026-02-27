import sqlite3
import random

class Database:
    def init(self, path):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.cur = self.conn.cursor()
        self.create_tables()

    def create_tables(self):
        self.cur.execute("""CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY,
                            name TEXT
                        )""")
        self.cur.execute("""CREATE TABLE IF NOT EXISTS questions (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            part TEXT,
                            question TEXT,
                            a TEXT, b TEXT, c TEXT, d TEXT,
                            correct TEXT
                        )""")
        self.conn.commit()

    def add_user(self, user_id, name):
        self.cur.execute("INSERT OR IGNORE INTO users (user_id, name) VALUES (?, ?)", (user_id, name))
        self.conn.commit()

    def get_user(self, user_id):
        self.cur.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
        return self.cur.fetchone()

    def get_random_questions(self, part, count):
        self.cur.execute("SELECT question, a, b, c, d, correct FROM questions WHERE part=?", (part,))
        all_questions = self.cur.fetchall()
        selected = random.sample(all_questions, min(len(all_questions), count))
        return [{"question": q[0], "a": q[1], "b": q[2], "c": q[3], "d": q[4], "correct": q[5]} for q in selected]
