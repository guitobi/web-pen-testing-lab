from __future__ import annotations
import sqlite3
import os

DB_PATH = "shop.db"

# Просто додаємо товари в існуючу таблицю products:
#   id INTEGER PRIMARY KEY AUTOINCREMENT,
#   name TEXT,
#   description TEXT,
#   price REAL

PRODUCTS = [
    # Ноутбуки та комп'ютери
    ("Lenovo ThinkBook 15",
     "Категорія: Ноутбуки та комп'ютери. Офісний ноутбук для роботи.",
     18999.0),
    ("HP Pavilion Gaming",
     "Категорія: Ноутбуки та комп'ютери. Ігровий ноутбук середнього класу.",
     27999.0),
    ("Acer Aspire 3",
     "Категорія: Ноутбуки та комп'ютери. Бюджетний ноутбук для навчання.",
     14999.0),

    # Смартфони, ТВ та електроніка
    ("Samsung Galaxy S21",
     "Категорія: Смартфони, ТВ та електроніка. Флагманський смартфон.",
     15999.0),
    ("iPhone 12",
     "Категорія: Смартфони, ТВ та електроніка. Смартфон Apple.",
     19999.0),
    ("Xiaomi Redmi Note 11",
     "Категорія: Смартфони, ТВ та електроніка. Бюджетний смартфон.",
     7999.0),

    # Товари для геймерів
    ("Logitech G102",
     "Категорія: Товари для геймерів. Ігрова мишка.",
     899.0),
    ("HyperX Cloud II",
     "Категорія: Товари для геймерів. Ігрові навушники.",
     2999.0),
    ("Razer Cynosa",
     "Категорія: Товари для геймерів. Мембранна геймерська клавіатура.",
     1599.0),

    # Побутова техніка
    ("Philips 7000",
     "Категорія: Побутова техніка. Електробритва для щоденного користування.",
     1299.0),
    ("Braun 5030s",
     "Категорія: Побутова техніка. Бритва з тримером.",
     2399.0),
    ("Dyson V8",
     "Категорія: Побутова техніка. Бездротовий пилосмок.",
     8999.0),

    # Одяг та аксесуари
    ("Casio F91W",
     "Категорія: Одяг та аксесуари. Легендарний цифровий годинник.",
     499.0),
    ("RayBan Aviator",
     "Категорія: Одяг та аксесуари. Сонцезахисні окуляри.",
     3499.0),
    ("Nike Backpack",
     "Категорія: Одяг та аксесуари. Міський рюкзак для щоденного користування.",
     1199.0),
]


def seed_products():
    if not os.path.exists(DB_PATH):
        raise FileNotFoundError("База даних shop.db не знайдена в корені проекту.")

    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    print("[*] Додаю тестові товари...")

    for name, desc, price in PRODUCTS:
        # Щоб не плодити дублі при повторному запуску - перевіряємо по name
        row = cur.execute(
            "SELECT id FROM products WHERE name = ?",
            (name,)
        ).fetchone()

        if row:
            print(f"[=] Вже існує: {name} (id={row[0]}), пропускаю.")
            continue

        cur.execute(
            "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
            (name, desc, price),
        )
        pid = cur.lastrowid
        print(f"[+] Додано товар id={pid}: {name}")

    conn.commit()
    conn.close()
    print("[✓] Готово! Тестові товари додано.")


if __name__ == "__main__":
    seed_products()
