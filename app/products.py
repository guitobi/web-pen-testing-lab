from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# !!! ВАЖЛИВО: Імпортуємо змінну з назвою таблиці з db.py
from .db import get_db, REAL_PRODUCT_TABLE

router = APIRouter(tags=["products"])

templates = Jinja2Templates(directory="app/template")


@router.get("/products")
def list_products(q: str | None = None):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- WAF: Блокуємо пробіли ---
    if q and " " in q:
        conn.close()
        return [{
            "id": 0, 
            "name": "⛔ WAF BLOCKED", 
            "description": "Security Error: Spaces are illegal characters! Use comments /**/ instead.", 
            "price": 0.0
        }]

    # !!! ВИКОРИСТОВУЄМО REAL_PRODUCT_TABLE ЗАМІСТЬ 'products'
    if q:
        query = (
            f"SELECT id, name, description, price FROM {REAL_PRODUCT_TABLE} "
            f"WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        )
    else:
        query = f"SELECT id, name, description, price FROM {REAL_PRODUCT_TABLE}"

    rows = []
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except sqlite3.Warning:
        # Дозволяємо DROP через скрипт (якщо юзер ввів крапку з комою)
        try:
            print(f"\n[DEBUG] ⚠️ Warning caught. Attempting script execution for: {q}")
            cur.executescript(query)
            conn.commit()
            print("[DEBUG] ✅ Script executed successfully! (Table potentially dropped)")
        except Exception as script_err:
             print(f"[ERROR] ❌ Script execution failed: {script_err}")
             pass
    except Exception as e:
        # !!! КРИТИЧНЕ ВИПРАВЛЕННЯ !!!
        # Якщо таблиця вже видалена, ми НЕ повинні ковтати цю помилку.
        # Ми повинні прокинути її далі, щоб main.py показав екран перемоги.
        if "no such table" in str(e).lower():
            raise e

        # Ловимо інші помилки, але теж пробуємо скрипт (на випадок DROP)
        try:
            print(f"\n[DEBUG] ⚠️ Exception caught ({e}). Attempting script execution...")
            cur.executescript(query)
            conn.commit()
            print("[DEBUG] ✅ Script executed successfully! (Table potentially dropped)")
        except Exception as script_err:
            print(f"[ERROR] ❌ Script execution failed: {script_err}")
            pass
        
        print(f"[INFO] Original SQL Error: {e}")

    conn.close()
    return [dict(r) for r in rows]


@router.get("/product", response_class=HTMLResponse)
def product_page(request: Request, id: int):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
        # !!! ТУТ ТЕЖ ЗМІНЮЄМО НАЗВУ НА СЕКРЕТНУ
        cur.execute(f"SELECT * FROM {REAL_PRODUCT_TABLE} WHERE id = {id}")
        product = cur.fetchone()
    except sqlite3.OperationalError:
        conn.close()
        raise

    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    cur.execute(
        f"SELECT author, text, '' AS created_at "
        f"FROM reviews WHERE product_id = {product['id']} ORDER BY id DESC"
    )
    reviews = cur.fetchall()
    conn.close()

    return templates.TemplateResponse(
        "vuln_shop/product.html",
        {
            "request": request,
            "product": product,
            "reviews": reviews,
        },
    )


@router.post("/add_review")
async def add_review(request: Request, id: int):
    form = await request.form()
    author = form.get("author", "")
    text = form.get("text", "")

    conn = get_db()
    cur = conn.cursor()

    try:
        cur.execute(
            f"INSERT INTO reviews (product_id, author, text) "
            f"VALUES ({id}, '{author}', '{text}')"
        )
        conn.commit()
    except sqlite3.OperationalError:
         conn.close()
         raise

    conn.close()
    return RedirectResponse(url=f"/product?id={id}", status_code=302)