from typing import Optional
from fastapi import APIRouter, HTTPException, Depends
from app.db import get_db
from app.schemas import ProductCreate, ReviewCreate
from app.auth import get_current_user

router = APIRouter(prefix="/products", tags=["products"])

@router.get("")
def list_products(q: Optional[str] = None):
    conn = get_db()
    cur = conn.cursor()

    if q:
        query = f"SELECT * FROM products WHERE name LIKE '%{q}%' OR description LIKE '%{q}%'"
    else:
        query = "SELECT * FROM products"

    rows = cur.execute(query).fetchall()
    conn.close()
    return [dict(r) for r in rows]

@router.get("/{product_id}")
def get_product(product_id: int):
    conn = get_db()
    cur = conn.cursor()
    query = f"SELECT * FROM products WHERE id = {product_id}"
    row = cur.execute(query).fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Product not found")
    return dict(row)

@router.post("")
def create_product(data: ProductCreate, current=Depends(get_current_user)):
    if not current or current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    conn = get_db()
    cur = conn.cursor()
    query = (
        f"INSERT INTO products (name, description, price) "
        f"VALUES ('{data.name}', '{data.description}', {data.price})"
    )
    cur.execute(query)
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return {"id": pid, **data.dict()}

@router.post("/{product_id}/reviews")
def add_review(product_id: int, data: ReviewCreate):
    conn = get_db()
    cur = conn.cursor()
    query = (
        f"INSERT INTO reviews (product_id, author, text) "
        f"VALUES ({product_id}, '{data.author}', '{data.text}')"
    )
    cur.execute(query)
    conn.commit()
    conn.close()
    return {"status": "ok"}

@router.get("/{product_id}/reviews")
def list_reviews(product_id: int):
    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute(f"SELECT * FROM reviews WHERE product_id = {product_id}").fetchall()
    conn.close()
    return [dict(r) for r in rows]
