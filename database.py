import aiosqlite

DB_NAME = "database.db"

async def init_db():
    async with aiosqlite.connect(DB_NAME) as db:
        await db.execute("""
        CREATE TABLE IF NOT EXISTS users(
            user_id INTEGER PRIMARY KEY,
            best_score REAL DEFAULT 0,
            total_tests INTEGER DEFAULT 0,
            average_score REAL DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS tests(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            creator_id INTEGER,
            name TEXT,
            timer INTEGER,
            usage_count INTEGER DEFAULT 0,
            best_score REAL DEFAULT 0,
            avg_score REAL DEFAULT 0
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS questions(
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            test_id INTEGER,
            question TEXT,
            a TEXT,
            b TEXT,
            c TEXT,
            d TEXT,
            correct TEXT
        )
        """)

        await db.execute("""
        CREATE TABLE IF NOT EXISTS creators(
            user_id INTEGER PRIMARY KEY,
            created_tests INTEGER DEFAULT 0
        )
        """)

        await db.commit()