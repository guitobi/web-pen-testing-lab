import sqlite3

DB_PATH = "shop.db"

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT,
            role TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER,
            author TEXT,
            text TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS orders (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            total REAL,
            items_json TEXT
        )
        """
    )

    cur.execute(
        "INSERT OR IGNORE INTO products (id, name, description, price) "
        "VALUES (1, 'Phone', '<b>Cheap phone</b>', 100.0)"
    )
    cur.execute(
        "INSERT OR IGNORE INTO products (id, name, description, price) "
        "VALUES (2, 'Laptop', '<script>alert(\"xss\")</script>', 999.0)"
    )

    conn.commit()
    conn.close()
