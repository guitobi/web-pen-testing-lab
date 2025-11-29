# app/main.py
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .db import init_db
from . import auth, products, orders, admin, auth_register
from .tsrouter import router as demo_router

# Run: uvicorn app.main:app --reload


app = FastAPI(title="Vulnerable Shop API")
templates = Jinja2Templates(directory="app/template")


@app.on_event("startup")
def on_startup():
    init_db()


# API
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(demo_router)
app.include_router(auth_register.router)

# static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---------- HTML pages ----------
@app.get("/")
def index_page(request: Request):
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
