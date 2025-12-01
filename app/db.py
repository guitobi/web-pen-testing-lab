import sqlite3
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH = BASE_DIR / "shop.db"

# CTF CHALLENGE: Секретна назва таблиці.
REAL_PRODUCT_TABLE = "data_inventory_v2_secure"

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    return conn

# --- ФУНКЦІЇ НАПОВНЕННЯ (SEEDING) ---

def seed_users(cur):
    users = [
        ("admin", "admin", "admin"),
        ("user", "password", "user"),
        ("alice", "alice123", "user"),
        ("bob", "123456", "user"),
    ]
    for username, password, role in users:
        cur.execute(
            "INSERT OR IGNORE INTO users (username, password, role) VALUES (?, ?, ?)",
            (username, password, role),
        )

def seed_products(cur):
    vuln_products = [
        (1, "Phone", "<b>Cheap phone</b>", 100.0, "523634223.webp"),
        (2, "Laptop", "Standard Laptop Description", 999.0, "noutbuk-microsoft-surface-laptop-6-135-zjw-00026-platinum-1024x768.webp"),
        (3, "Gaming Mouse", "Ultra DPI mouse.", 49.99, "1200W-18684-Black-0-NKDH7709BlackBagFront3.jpg"),
        (4, "4K TV", "Big 4K TV.", 799.0, "big-tv.jpg"),
        (5, "Headphones", "Nice headphones.", 59.0, "fa0575c2-1397-4467-ba48-e18f84ed6c19.jpg"),
        (6, "CTF Hint", "You found the hidden table! Now DROP it to win.", 0.0, "favicon.png"),
    ]

    real_products = [
        (10, "Lenovo ThinkBook 15", "Категорія: Ноутбуки та комп'ютери. Офісний ноутбук для роботи.", 18999.0, "37-lenovo-thinkbook-15-hero.avif"),
        (11, "HP Pavilion Gaming", "Категорія: Ноутбуки та комп'ютери. Ігровий ноутбук середнього класу.", 27999.0, "21001517599382.jpg"),
        (12, "Acer Aspire 3", "Категорія: Ноутбуки та комп'ютери. Бюджетний ноутбук для навчання.", 14999.0, "21218-xW.jpg"),

        (20, "Samsung Galaxy S21", "Категорія: Смартфони, ТВ та електроніка. Флагманський смартфон.", 15999.0, "201230150040321987.webp"),
        (21, "iPhone 12", "Категорія: Смартфони, ТВ та електроніка. Смартфон Apple.", 19999.0, "210428160019905946.webp"),
        (22, "Xiaomi Redmi Note 11", "Категорія: Смартфони, ТВ та електроніка. Бюджетний смартфон.", 7999.0, "333623502.webp"),

        (30, "Logitech G102", "Категорія: Товари для геймерів. Ігрова мишка.", 899.0, "1400_gallery_1716317775110291_0.webp"),
        (31, "HyperX Cloud II", "Категорія: Товари для геймерів. Ігрові навушники.", 2999.0, "fa0575c2-1397-4467-ba48-e18f84ed6c19.jpg"),
        (32, "Razer Cynosa", "Категорія: Товари для геймерів. Мембранна геймерська клавіатура.", 1599.0, "3470132825.jpg"),

        (40, "Philips 7000", "Категорія: Побутова техніка. Електробритва.", 1299.0, "main-1-528x396.jpg"),
        (41, "Braun 5030s", "Категорія: Побутова техніка. Бритва з тримером.", 2399.0, "sovershenstvu_est_predel_-_braun_5030_s.jpg"),
        (42, "Dyson V8", "Категорія: Побутова техніка. Бездротовий пилосмок.", 8999.0, "pilosos_Dyson_V8_Total_Clean-947237-600x600.jpg"),

        (50, "Casio F91W", "Категорія: Одяг та аксесуари. Годинник.", 499.0, "image.avif"),
        (51, "RayBan Aviator", "Категорія: Одяг та аксесуари. Окуляри.", 3499.0, "getimg.jpg"),
        (52, "Nike Backpack", "Категорія: Одяг та аксесуари. Міський рюкзак.", 1199.0, "1200W-18684-Black-0-NKDH7709BlackBagFront3.jpg"),
    ]

    all_products = vuln_products + real_products

    for pid, name, desc, price, img in all_products:
        cur.execute(
            f"""
            INSERT OR IGNORE INTO {REAL_PRODUCT_TABLE}
            (id, name, description, price, image)
            VALUES (?, ?, ?, ?, ?)
            """,
            (pid, name, desc, price, img),
        )

def seed_reviews(cur):
    # Перевіряємо, чи таблиця пуста, щоб не дублювати відгуки при кожному запуску
    cur.execute("SELECT count(*) FROM reviews")
    if cur.fetchone()[0] > 0:
        return

    # Тут теж прибрали XSS з тексту відгуків
    reviews = [
        (1, "user", "Нормальний телефон за свої гроші."),
        (1, "alice", "Супер! Але заряд тримає мало."),
        (2, "pentester", "Just a regular review."),
        (3, "bob", "Click here for details."),
        (4, "admin", "Офіційна знижка тільки сьогодні!"),
        (5, "xss", "Another safe review."),
        (20, "alice", "Камера просто топ!"),
        (30, "user", "Мишка зручна, сенсор не зриває."),
        (42, "admin", "Трохи дорого, але воно того варте."),
    ]
    for product_id, author, text in reviews:
        cur.execute(
            "INSERT INTO reviews (product_id, author, text) VALUES (?, ?, ?)",
            (product_id, author, text),
        )

def seed_orders(cur):
    # Перевіряємо, чи таблиця пуста
    cur.execute("SELECT count(*) FROM orders")
    if cur.fetchone()[0] > 0:
        return

    orders = [
        (2, 100.0, json.dumps([{"product_id": 1, "qty": 1, "price": 100.0}])),
        (3, 49.99, json.dumps([{"product_id": 3, "qty": 1, "price": 49.99}])),
        (1, 0.01, json.dumps([{"product_id": 4, "qty": 1, "price": 0.01}])),
    ]
    for user_id, total, items_json in orders:
        cur.execute(
            "INSERT INTO orders (user_id, total, items_json) VALUES (?, ?, ?)",
            (user_id, total, items_json),
        )

# --- ГОЛОВНА ФУНКЦІЯ ІНІЦІАЛІЗАЦІЇ ---

def init_db():
    conn = get_db()
    cur = conn.cursor()

    # 1. Створення таблиць
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
    
    # Створення секретної таблиці товарів
    cur.execute(
        f"""
        CREATE TABLE IF NOT EXISTS {REAL_PRODUCT_TABLE} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            description TEXT,
            price REAL,
            image TEXT

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

    # 2. Автоматичне наповнення даними
    try:
        seed_users(cur)
        seed_products(cur)
        seed_reviews(cur)
        seed_orders(cur)
        conn.commit()
    except Exception as e:
        print(f"DB Init Error: {e}")
    finally:
        conn.close()