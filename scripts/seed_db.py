# seed_db.py
from __future__ import annotations

import json
import sys
import os
import sqlite3
from pathlib import Path

# Додаємо корінь проекту у sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db import get_db, init_db, REAL_PRODUCT_TABLE

def seed_users(cur):
    """
    Створюємо користувачів.
    """
    print(f"[*] Seeding users...")
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
    """
    Додаємо товари у СЕКРЕТНУ таблицю.
    Тут прибрано XSS (alert), щоб не дратувати при перезавантаженні.
    """
    print(f"[*] Seeding products into hidden table '{REAL_PRODUCT_TABLE}'...")
    products = [
        (1, "Phone", "<b>Cheap phone</b>", 100.0),
        # БУЛО: <script>alert("xss from description")</script>
        (2, "Laptop", "Standard Laptop Description", 999.0), 
        # БУЛО: <img src="x" onerror="alert('xss img')">
        (3, "Gaming Mouse", "Ultra DPI mouse.", 49.99),
        # БУЛО: <a href='javascript:alert(1)'>details</a>
        (4, "4K TV", "Big <i>4K</i> TV. Great details.", 799.0),
        (5, "Headphones", "Nice headphones.", 59.0),
        
        # Товар-підказка для CTF залишається
        (6, "CTF Hint", "You found the hidden table! Now DROP it to win.", 0.0),
    ]

    for pid, name, desc, price in products:
        cur.execute(
            f"INSERT OR IGNORE INTO {REAL_PRODUCT_TABLE} (id, name, description, price) VALUES (?, ?, ?, ?)",
            (pid, name, desc, price),
        )

def seed_reviews(cur):
    print(f"[*] Seeding reviews...")
    reviews = [
        (1, "user", "Нормальний телефон за свої гроші."),
        (1, "alice", "<b>Супер!</b> Але заряд тримає мало."),
        # Прибрано XSS з відгуків
        (2, "pentester", "Just a regular review without scripts."),
        (3, "bob", "Click here for details: link."),
        (4, "admin", "Офіційна знижка тільки сьогодні!"),
        (5, "xss", "Another safe review."),
    ]

    for product_id, author, text in reviews:
        cur.execute(
            "INSERT INTO reviews (product_id, author, text) VALUES (?, ?, ?)",
            (product_id, author, text),
        )

def seed_orders(cur):
    print(f"[*] Seeding orders...")
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

def main():
    # 1. Ініціалізуємо БД
    init_db()

    conn = get_db()
    cur = conn.cursor()

    try:
        seed_users(cur)
        seed_products(cur)
        seed_reviews(cur)
        seed_orders(cur)
        conn.commit()
        print("✅ DB seeded successfully (NO ALERTS)!")
    except Exception as e:
        print(f"❌ Error seeding DB: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    main()