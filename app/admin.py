# app/admin.py
import sqlite3
from fastapi import APIRouter, HTTPException, Depends, Form, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

# !!! ДОДАЛИ ІМПОРТ REAL_PRODUCT_TABLE
from app.db import get_db, init_db, REAL_PRODUCT_TABLE
from app.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])
templates = Jinja2Templates(directory="app/template")

@router.get("/", response_class=HTMLResponse)
def admin_panel_page(request: Request, current=Depends(get_current_user)):
    """
    Головна сторінка адмінки.
    """
    if not current or current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Access Denied: Admins Only")

    conn = get_db()
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()
    
    users_rows = cur.execute("SELECT id, username, role FROM users").fetchall()
    conn.close()

    return templates.TemplateResponse(
        "vuln_shop/admin_panel.html",
        {
            "request": request,
            "user": current,
            "users": users_rows
        }
    )

@router.post("/cleanup")
def cleanup_table(request: Request, table_name: str = Form(...), current=Depends(get_current_user)):
    """
    Вразлива функція. Видаляє таблицю і одразу перевіряє, чи жива БД.
    """
    if not current or current["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin only")

    conn = get_db()
    cur = conn.cursor()

    try:
        # 1. Виконуємо видалення (як і раніше)
        query = f"DROP TABLE IF EXISTS {table_name}"
        print(f"[ADMIN] Executing: {query}")
        cur.execute(query)
        conn.commit()

        # 2. !!! НОВА ПЕРЕВІРКА !!!
        # Ми намагаємося прочитати дані з ГОЛОВНОЇ таблиці товарів.
        # Якщо ми щойно її видалили (через table_name), цей запит впаде з помилкою.
        cur.execute(f"SELECT 1 FROM {REAL_PRODUCT_TABLE} LIMIT 1")
        
    except sqlite3.OperationalError as e:
        # Якщо помилка "no such table", ми її прокидаємо (raise),
        # щоб main.py перехопив її і показав Victory Screen.
        if "no such table" in str(e).lower():
            raise e
        pass
    finally:
        conn.close()

    return RedirectResponse(url="/admin/", status_code=303)

# --- CTF RESTORE ---
@router.post("/restore_db")
def restore_database():
    try:
        init_db()
        return RedirectResponse(url="/", status_code=302)
    except Exception as e:
        return {"status": "error", "detail": str(e)}