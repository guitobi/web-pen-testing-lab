from typing import Optional
from fastapi import APIRouter, HTTPException, Header
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

def get_current_user(authorization: Optional[str] = Header(None)):
    if not authorization:
        return None

    parts = authorization.split()
    if len(parts) == 2 and parts[0].lower() == "bearer":
        username = parts[1]
    else:
        username = authorization

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
