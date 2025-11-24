import json
from fastapi import APIRouter, HTTPException, Depends
from app.db import get_db
from app.schemas import CheckoutRequest
from app.auth import get_current_user

router = APIRouter(tags=["orders"])

@router.post("/cart/checkout")
def checkout(data: CheckoutRequest, current=Depends(get_current_user)):
    if not current:
        raise HTTPException(status_code=401, detail="Login required")

    user_id = current["id"]
    items_json = json.dumps([item.dict() for item in data.items])

    conn = get_db()
    cur = conn.cursor()
    query = (
        f"INSERT INTO orders (user_id, total, items_json) "
        f"VALUES ({user_id}, {data.total}, '{items_json}')"
    )
    cur.execute(query)
    conn.commit()
    oid = cur.lastrowid
    conn.close()
    return {"order_id": oid, "total": data.total}

@router.get("/orders/{order_id}")
def get_order(order_id: int, current=Depends(get_current_user)):
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute(f"SELECT * FROM orders WHERE id = {order_id}").fetchone()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Order not found")
    return dict(row)
