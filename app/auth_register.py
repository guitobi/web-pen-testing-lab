from typing import Optional
from fastapi import APIRouter, HTTPException, Header, Request, Response
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])

def get_current_user(request: Request, authorization: Optional[str] = Header(None)):
    token = None
    if authorization:
        parts = authorization.split()
        if len(parts) == 2 and parts[0].lower() == "bearer":
            token = parts[1]
        else:
            token = authorization
    
    if not token:
        token = request.cookies.get("token")

    if not token:
        return None

    username = token
    conn = get_db()
    cur = conn.cursor()
    row = cur.execute(f"SELECT id, username, role FROM users WHERE username = '{username}'").fetchone()
    conn.close()

    if not row:
        return None

    return {"id": row["id"], "username": row["username"], "role": row["role"]}

@router.post("/login")
def login(data: LoginRequest, response: Response):
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
    
    # Дублюємо встановлення куки на сервері (для надійності)
    response.set_cookie(key="token", value=token, httponly=False, path="/", max_age=3600)
    
    return {"token": token, "role": user["role"]}

# !!! НОВИЙ ЕНДПОІНТ ДЛЯ ВИХОДУ !!!
@router.get("/logout")
def logout(response: Response):
    # Ця команда змушує браузер видалити куку
    response.delete_cookie(key="token", path="/")
    return {"message": "Logged out successfully"}