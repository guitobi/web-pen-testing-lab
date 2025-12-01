from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException, Request, Form, Depends
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

# Імпортуємо змінну з назвою таблиці
from .db import get_db, REAL_PRODUCT_TABLE
from app.auth import get_current_user

router = APIRouter(tags=["products"])

templates = Jinja2Templates(directory="app/template")


@router.get("/products")
def list_products(q: str | None = None):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # --- WAF: ВИМКНЕНО (для зручності навчання) ---
    # if q and " " in q:
    #     conn.close()
    #     return ...

    # !!! ВАЖЛИВО: додаємо image у вибірку (для відображення картинок)
    if q:
        query = (
            f"SELECT id, name, description, price, image FROM {REAL_PRODUCT_TABLE} "
            f"WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        )
    else:
        query = f"SELECT id, name, description, price, image FROM {REAL_PRODUCT_TABLE}"

    rows = []
    try:
        cur.execute(query)
        rows = cur.fetchall()
    except sqlite3.Warning:
        try:
            # Спроба виконати скрипт, якщо SQLite видав попередження (Stack Queries)
            print(f"\n[DEBUG] ⚠️ Warning caught. Attempting script execution...")
            cur.executescript(query)
            conn.commit()
        except Exception:
             pass
    except Exception as e:
        # Якщо таблицю видалили - прокидаємо помилку для екрану перемоги
        if "no such table" in str(e).lower():
            raise e
        try:
            cur.executescript(query)
            conn.commit()
        except Exception:
            pass

    conn.close()
    return [dict(r) for r in rows]


@router.get("/product", response_class=HTMLResponse)
def product_page(request: Request, id: int):
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    try:
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
            f"INSERT INTO reviews (product_id, author, text) VALUES ({id}, '{author}', '{text}')"
        )
        conn.commit()
    except sqlite3.OperationalError:
         conn.close()
         raise

    conn.close()
    return RedirectResponse(url=f"/product?id={id}", status_code=302)


# --- ВРАЗЛИВИЙ ЕНДПОІНТ (BROKEN ACCESS CONTROL) ---
@router.post("/product/update")
def update_product_info(
    id: int = Form(...), 
    name: str = Form(...), 
    price: float = Form(...), 
    current=Depends(get_current_user)
):
    """
    Вразливість: Broken Access Control (BAC).
    Будь-який залогінений користувач може редагувати товари.
    """
    # 1. Перевірка: чи користувач взагалі залогінений?
    if not current:
        raise HTTPException(status_code=401, detail="Login required")

    # 2. ВРАЗЛИВІСТЬ: ТУТ МАЛА БУТИ ПЕРЕВІРКА НА АДМІНА!
    # if current['role'] != 'admin':
    #     raise HTTPException(status_code=403, detail="Admins only")
    # АЛЕ ЇЇ НЕМАЄ :)
    
    conn = get_db()
    cur = conn.cursor()

    try:
        # Також тут є SQL Injection через параметр name
        query = f"UPDATE {REAL_PRODUCT_TABLE} SET name = '{name}', price = {price} WHERE id = {id}"
        cur.execute(query)
        conn.commit()
    except Exception as e:
        conn.close()
        return {"status": "error", "detail": str(e)}

    conn.close()
    return RedirectResponse(url=f"/product?id={id}", status_code=303)