from fastapi import APIRouter, HTTPException, Depends
from app.db import get_db
from app.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/users")
def admin_list_users(current=Depends(get_current_user)):
    if not current or current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    conn = get_db()
    cur = conn.cursor()
    rows = cur.execute("SELECT id, username, password, role FROM users").fetchall()
    conn.close()
    return [dict(r) for r in rows]
