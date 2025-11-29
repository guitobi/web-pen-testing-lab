# app/auth_register.py
from fastapi import APIRouter, HTTPException
from app.db import get_db
from app.schemas import LoginRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(data: LoginRequest, role: str = "user"):
    """
    Дуже проста і дуже вразлива реєстрація.

    Вразливості:
    - SQL injection в SELECT та INSERT, бо параметри ліпляться в f-строки без екранування.
    - Збереження паролю у відкритому вигляді (plain text), без хешування.
    - Поле role береться з query параметра без перевірки, тобто
      /auth/register?role=admin дає змогу створити адміна.
    """

    conn = get_db()
    cur = conn.cursor()

    # VULN 1: SQL injection при перевірці існування юзера
    exists = cur.execute(
        f"SELECT id FROM users WHERE username = '{data.username}'"
    ).fetchone()

    if exists:
        conn.close()
        raise HTTPException(status_code=400, detail="User already exists")

    # VULN 2: SQL injection в INSERT
    # VULN 3: пароль вставляється як є, без хешу
    # VULN 4: role повністю контролюється користувачем через query параметр
    cur.execute(
        f"INSERT INTO users (username, password, role) "
        f"VALUES ('{data.username}', '{data.password}', '{role}')"
    )

    conn.commit()
    conn.close()

    return {
        "status": "ok",
        "msg": "account created",
        "debug_note": "registration is intentionally vulnerable (SQLi, plain password, role tampering)",
    }
