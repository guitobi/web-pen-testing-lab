# app/auth.py
from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Request, Depends
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

# !!! ГОЛОВНА ЗМІНА: Додали request: Request, щоб читати куки !!!
def get_current_user(request: Request, authorization: Optional[str] = Header(None)):
    token = None
    
    # 1. Спочатку шукаємо в заголовку (для fetch запитів)
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = authorization
    
    # 2. Якщо в заголовку пусто, шукаємо в COOKIES (для браузера)
    if not token:
        token = request.cookies.get("token")

    if not token:
        return None

    # У цьому CTF токен = юзернейм
    username = token

    conn = get_db()
    cur = conn.cursor()
    query = f"SELECT id, username, role FROM users WHERE username = '{username}'"
    row = cur.execute(query).fetchone()
    conn.close()

    if not row:
        return None

    return {"id": row["id"], "username": row["username"], "role": row["role"]}

@router.post("/login")
def login(data: LoginRequest):
    conn = get_db()
    cur = conn.cursor()
    query = (
        f"SELECT id, username, role FROM users "
        f"WHERE username = '{data.username}' AND password = '{data.password}'"
    )
    user = cur.execute(query).fetchone()
    conn.close()

    if not user:
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = user["username"]
    return {"token": token, "role": user["role"]}