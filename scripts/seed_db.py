# seed_db.py
from __future__ import annotations

import json
from pathlib import Path

import sys
import os

# додаємо корінь проекту у sys.path
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from app.db import get_db, init_db

def seed_users(cur):
    """
    Створюємо кілька користувачів зі СЛАБКИМИ паролями (без хешування).
    Це спеціально для демонстрації Broken Auth.
    """
    users = [
        # username, password, role
        ("admin", "admin", "admin"),
        ("user", "password", "user"),
        ("alice", "alice123", "user"),
        ("bob", "123456", "user"),
    ]

    for username, password, role in users:
        # VULN: паролі у відкритому вигляді, без солі, без хешу
        cur.execute(
            """
            INSERT OR IGNORE INTO users (username, password, role)
            VALUES (?, ?, ?)
            """,
            (username, password, role),
        )


def seed_products(cur):
    """
    Додаємо кілька товарів.
    Частина описів спеціально містить HTML/XSS для демонстрації stored XSS.
    """
    products = [
        # id, name, description, price
        (1, "Phone", "<b>Cheap phone</b>", 100.0),
        (
            2,
            "Laptop",
            '<script>alert("xss from description")</script>',
            999.0,
        ),
        (
            3,
            "Gaming Mouse",
            'Ultra DPI mouse.<br><img src="x" onerror="alert(\'xss img\')">',
            49.99,
        ),
        (
            4,
            "4K TV",
            "Big <i>4K</i> TV. <a href='javascript:alert(1)'>details</a>",
            799.0,
        ),
        (
            5,
            "Headphones",
            "Nice headphones with &lt;no script&gt; (але можна вставити свій відгук).",
            59.0,
        ),
    ]

    for pid, name, desc, price in products:
        cur.execute(
            """
            INSERT OR IGNORE INTO products (id, name, description, price)
            VALUES (?, ?, ?, ?)
            """,
            (pid, name, desc, price),
        )


def seed_reviews(cur):
    """
    Додаємо кілька відгуків, включно з XSS.
    """
    reviews = [
        # product_id, author, text
        (1, "user", "Нормальний телефон за свої гроші."),
        (1, "alice", "<b>Супер!</b> Але заряд тримає мало."),
        (2, "pentester", '<script>alert("stored xss review")</script>'),
        (3, "bob", 'Клікни сюди: <a href="javascript:alert(1337)">link</a>'),
        (4, "admin", "Офіційна знижка тільки сьогодні!"),
        (5, "xss", '<img src=x onerror="alert(\'img xss from review\')">'),
    ]

    for product_id, author, text in reviews:
        cur.execute(
            """
            INSERT INTO reviews (product_id, author, text)
            VALUES (?, ?, ?)
            """,
            (product_id, author, text),
        )


def seed_orders(cur):
    """
    Пара тестових замовлень з items_json – для демонстрації логічних багів / IDOR.
    """
    orders = [
        # user_id, total, items_json
        (
            2,  # user
            100.0,
            json.dumps([{"product_id": 1, "qty": 1, "price": 100.0}]),
        ),
        (
            3,  # alice
            49.99,
            json.dumps([{"product_id": 3, "qty": 1, "price": 49.99}]),
        ),
        (
            1,  # admin
            0.01,  # підозріло низька ціна - для демонстрації logic flaw
            json.dumps([{"product_id": 4, "qty": 1, "price": 0.01}]),
        ),
    ]

    for user_id, total, items_json in orders:
        cur.execute(
            """
            INSERT INTO orders (user_id, total, items_json)
            VALUES (?, ?, ?)
            """,
            (user_id, total, items_json),
        )


def main():
    # Переконуємось, що таблиці створені
    init_db()

    conn = get_db()
    cur = conn.cursor()

    seed_users(cur)
    seed_products(cur)
    seed_reviews(cur)
    seed_orders(cur)

    conn.commit()
    conn.close()

    print("✅ DB seeded with demo users, products, reviews and orders.")


if __name__ == "__main__":
    # переконуємось, що запускаємо з кореня проєкту
    proj_root = Path(__file__).resolve().parent
    print(f"Using DB in: {proj_root / 'shop.db'}")
    main()
