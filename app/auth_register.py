from fastapi import APIRouter, HTTPException
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register")
def register(data: LoginRequest):
    conn = get_db()
    cur = conn.cursor()

    # SQL injection можливий тут
    exists = cur.execute(
        f"SELECT id FROM users WHERE username = '{data.username}'"
    ).fetchone()

    if exists:
        raise HTTPException(status_code=400, detail="User already exists")

    # теж SQL injection, теж без фільтрів
    cur.execute(
        f"INSERT INTO users (username, password, role) "
        f"VALUES ('{data.username}', '{data.password}', 'user')"
    )
    conn.commit()
    conn.close()

    return {"status": "ok", "msg": "account created"}