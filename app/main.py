# app/main.py
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from .db import init_db
from . import auth, products, orders, admin
from .tsrouter import router as demo_router

app = FastAPI(title="Vulnerable Shop API")


@app.on_event("startup")
def on_startup():
    init_db()


# API
app.include_router(auth.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(admin.router)
app.include_router(demo_router)

# static
app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ---------- HTML сторінки ----------

@app.get("/", response_class=FileResponse)
def index_page():
    return FileResponse("app/template/vuln_shop/index.html")


@app.get("/login", response_class=FileResponse)
def login_page():
    return FileResponse("app/template/vuln_shop/login.html")


@app.get("/product", response_class=FileResponse)
def product_page():
    # JS сам читає ?id= з query
    return FileResponse("app/template/vuln_shop/product.html")
