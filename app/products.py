# app/products.py
from __future__ import annotations

import sqlite3

from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates

from .db import get_db

router = APIRouter(tags=["products"])

templates = Jinja2Templates(directory="app/template")


@router.get("/products")
def list_products(q: str | None = None):
    """
    Returns a list of products. The q filter is intentionally concatenated to SQL to demo SQLi.
    """
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    if q:
        query = (
            "SELECT id, name, description, price FROM products "
            f"WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
        )
    else:
        query = "SELECT id, name, description, price FROM products"

    cur.execute(query)
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]


@router.get("/product", response_class=HTMLResponse)
def product_page(request: Request, id: int):
    """
    Product detail page: intentionally vulnerable to SQLi via id and stored XSS via reviews.
    """
    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # VULN: SQL Injection (id concatenated into SQL)
    cur.execute(f"SELECT * FROM products WHERE id = {id}")
    product = cur.fetchone()
    if not product:
        conn.close()
        raise HTTPException(status_code=404, detail="Product not found")

    # Stored XSS rendered via {{ r.text|safe }}
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
    """
    Stores a review for the product with no sanitization (intentional stored XSS playground).
    """
    form = await request.form()
    author = form.get("author", "")
    text = form.get("text", "")

    conn = get_db()
    cur = conn.cursor()

    cur.execute(
        f"INSERT INTO reviews (product_id, author, text) "
        f"VALUES ({id}, '{author}', '{text}')"
    )
    conn.commit()
    conn.close()

    return RedirectResponse(url=f"/product?id={id}", status_code=302)
