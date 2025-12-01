from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import RedirectResponse
from app.db import get_db, init_db
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

# --- CTF RESTORE ---
@router.post("/restore_db")
def restore_database():
    try:
        init_db()
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        return {"status": "error", "detail": str(e)}