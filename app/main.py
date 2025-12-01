# app/main.py
import sqlite3
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import JSONResponse, PlainTextResponse

# Імпортуємо REAL_PRODUCT_TABLE
from .db import init_db, get_db, REAL_PRODUCT_TABLE
from . import auth, products, orders, admin, auth_register
from .tsrouter import router as demo_router

app = FastAPI(title="Vulnerable Shop API")
templates = Jinja2Templates(directory="app/template")

@app.on_event("startup")
def on_startup():
    init_db()

# --- CTF VICTORY HANDLER ---
@app.exception_handler(sqlite3.OperationalError)
async def db_crash_handler(request: Request, exc: sqlite3.OperationalError):
    error_msg = str(exc).lower()
    
    # Якщо помилка про відсутність таблиці - показуємо перемогу
    if "no such table" in error_msg:
        try:
            return templates.TemplateResponse(
                "vuln_shop/db_dropped.html", 
                {
                    "request": request,
                    "error_debug": str(exc)
                },
                status_code=200
            )
        except Exception:
            # Спрощений варіант: просто текст, щоб не плутатися в HTML-дужках
            return PlainTextResponse(
                f"DATABASE DESTROYED!\n\nВітаємо! Ви успішно видалили таблицю.\n(Файл шаблону db_dropped.html не знайдено, але перемога зарахована)\n\nDebug: {exc}",
                status_code=200
            )
    
    return JSONResponse(
        status_code=500,
        content={"detail": "Database Operational Error", "error": str(exc)},
    )

# Підключення роутерів
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(demo_router)
app.include_router(auth_register.router)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

@app.get("/")
def index_page(request: Request):
    """
    Головна сторінка. Перевіряє, чи жива база.
    """
    conn = get_db()
    try:
        # Перевіряємо існування таблиці
        conn.execute(f"SELECT 1 FROM {REAL_PRODUCT_TABLE} LIMIT 1")
    except sqlite3.OperationalError as e:
        if "no such table" in str(e).lower():
            # Якщо таблиці немає - кидаємо помилку, щоб зловив хендлер
            raise e
    finally:
        conn.close()

    return templates.TemplateResponse(
        "vuln_shop/index.html",
        {"request": request},
    )

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "vuln_shop/login.html",
        {"request": request},
    )

@app.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "vuln_shop/register.html",
        {"request": request},
    )