import sqlite3

# Initializes a SQLite3 database for storing each conversion request.
# For each request the original GrabCraft URL, the requester IP address and all the informations derived from the request are stored.


class StatsDB:
    db_path: str
    conn: sqlite3.Connection
    cursor: sqlite3.Cursor

    def __init__(self, db_path):
        self.db_path = db_path
        self.conn = sqlite3.connect(self.db_path)
        self.cursor = self.conn.cursor()

    def __enter__(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS requests(
                id INTEGER PRIMARY KEY,
                url TEXT,
                ip_address TEXT,
                timestamp INTEGER,
                browser TEXT,
                operating_system TEXT,
                referrer TEXT,
                user_agent TEXT
            );
        ''')
        self.conn.commit()

        return self

    def __exit__(self, type, value, traceback):
        self.conn.commit()
        self.conn.close()

    def track_request(self, url: str, ip_address: str, timestamp: int, browser: str, operating_system: str, referrer: str, user_agent: str):
        self.cursor.execute('''
            INSERT INTO requests(url, ip_address, timestamp, browser, operating_system, referrer, user_agent)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (url, ip_address, timestamp, browser, operating_system, referrer, user_agent))
        self.conn.commit()
