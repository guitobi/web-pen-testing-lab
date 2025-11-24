from __future__ import annotations

import os
from typing import Optional

import requests
from fastapi import (
    APIRouter,
    Depends,
    Form,
    File,
    UploadFile,
    HTTPException,
)
from fastapi.responses import HTMLResponse, PlainTextResponse, JSONResponse

from app.auth import get_current_user

router = APIRouter(
    prefix="/demo",
    tags=["vuln-demo"],
)


# ============= 1) Reflected XSS =============

@router.get("/reflected-xss", response_class=HTMLResponse)
async def reflected_xss(q: Optional[str] = ""):
    """
    Дуже простий приклад reflected XSS:
    - рядок q відображається напряму в HTML
    - ніякого екранування символів немає

    Приклад URL:
    /demo/reflected-xss?q=<script>alert(1)</script>
    """

    # VULN: Вставляємо q прямо в HTML (жодного escaping)
    return f"""
    <html>
        <head><title>Reflected XSS demo</title></head>
        <body>
            <h1>Reflected XSS</h1>
            <p>Ваш пошуковий запит:</p>
            <div>{q}</div>
            <p><a href="/demo/reflected-xss">Очистити</a></p>
        </body>
    </html>
    """


# ============= 2) CSRF (немає токена) =============

@router.post("/csrf-transfer")
async def csrf_transfer(
    to: str = Form(...),
    amount: float = Form(...),
    current=Depends(get_current_user),
):
    """
    "Грошовий" переказ:
    - немає жодного CSRF-токена
    - немає підтвердження дії
    - якщо браузер автоматично шле cookies/Authorization - це ідеальний CSRF-ендпоінт
    """

    if not current:
        raise HTTPException(status_code=401, detail="Login required")

    from_user = current["username"]

    # VULN: Ніяких перевірок балансу, підписів, CSRF-токенів і тд.
    # Просто "переказуємо" (насправді тут фейкова відповідь).
    return {
        "status": "ok",
        "from": from_user,
        "to": to,
        "amount": amount,
        "note": "CSRF vulnerable endpoint (no CSRF token, no confirmation)",
    }


# ============= 3) IDOR (Insecure Direct Object Reference) =============

# фейкові "баланси користувачів" тільки в пам'яті
FAKE_BALANCES = {
    "admin": 1_000_000.0,
    "user": 42.0,
    "alice": 777.0,
    "bob": 0.5,
}


@router.get("/balance/{username}")
async def get_balance(username: str, current=Depends(get_current_user)):
    """
    IDOR:
    - будь-який залогінений користувач може запросити баланс будь-якого username
    - немає перевірки, що `username == current["username"]`

    Приклади:
    /demo/balance/user
    /demo/balance/admin
    """

    if not current:
        raise HTTPException(status_code=401, detail="Login required")

    # VULN: ми просто читаємо баланс за username з URL,
    # а не за реальним користувачем current["username"]
    balance = FAKE_BALANCES.get(username, 0.0)

    return {
        "requested_username": username,
        "current_user": current["username"],
        "balance": balance,
        "note": "IDOR: no check that requested user == current user",
    }


# ============= 4) File Upload (без перевірок) =============

UPLOAD_DIR = "uploads"  # корінь для завантажень


@router.post("/upload", response_class=PlainTextResponse)
async def upload_file(file: UploadFile = File(...)):
    """
    Небезпечний upload:
    - довіряємо file.filename
    - не перевіряємо розширення/тип/розмір
    - можемо легко дозволити завантаження .php/.exe/.html тощо
    """

    os.makedirs(UPLOAD_DIR, exist_ok=True)

    # VULN: filename йде напряму в файлову систему.
    # Без нормалізації/обмеження це місце для path traversal та RCE (залежно від сервера).
    save_path = os.path.join(UPLOAD_DIR, file.filename)

    content = await file.read()
    with open(save_path, "wb") as f:
        f.write(content)

    return (
        f"Saved file as: {save_path}\n"
        "VULN: no extension/size/content validation, trusts filename from user."
    )


# ============= 5) SSRF (проксі до довільного URL) =============

@router.get("/ssrf")
async def ssrf_proxy(url: str):
    """
    SSRF-подібний ендпоінт:
    - бере параметр url з GET
    - робить запит до нього з сервера
    - повертає raw-текст відповіді

    Приклад:
    /demo/ssrf?url=http://example.com
    """

    try:
        # VULN: ніяких обмежень на схему/хост/порт.
        # Можна ходити на внутрішні адреси типу http://127.0.0.1:... або 169.254.x.x
        resp = requests.get(url, timeout=5)
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Request failed: {e}")

    # повертаємо перші N байтів, щоб не вбити браузер
    text = resp.text[:2000]

    return PlainTextResponse(
        text,
        media_type="text/plain; charset=utf-8",
        headers={"X-Source-URL": url},
    )
