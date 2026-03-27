from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from starlette.middleware.sessions import SessionMiddleware

from dotenv import load_dotenv
from datetime import date, datetime
from jinja2 import pass_context
import os
import json

from app.core.inject_template import AuthRedirectMiddleware, template_context
from app.auth.login_routes import router as login_router
from app.routes import router as api_router
from app.core.i18n import get_i18n_value
from app.core.logger import log

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret-key")
APP_VERSION = os.getenv("APP_VERSION", "1.0.0")


# ---------------------------------------------------------
# 1. Создание приложения
# ---------------------------------------------------------
app = FastAPI(
    title=" Информаицонно-разъяснительная работа",
    version=APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)
#Swagger UI: http://127.0.0.1/docs (127.0.0.1 in Bing)
#ReDoc: http://127.0.0.1/redoc (127.0.0.1 in Bing)

# ---------------------------------------------------------
# 2. Jinja2 Templates
# ---------------------------------------------------------
templates = Jinja2Templates(directory="app/templates")


@pass_context
def res_value(ctx, key):
    request = ctx["request"]
    lang = request.session.get("lang", "ru")
    return get_i18n_value(lang, key)


templates.env.globals["res_value"] = res_value

# --- Filters ---
def filter_date(value):
    if isinstance(value, (date, datetime)):
        return value.strftime("%Y-%m-%d")
    return value or ""

def filter_json(value):
    try:
        return json.dumps(value, ensure_ascii=False)
    except:
        return ""

templates.env.filters["date"] = filter_date
templates.env.filters["json"] = filter_json


# templates.env.globals["ctx"] = template_context
# Example:
# {% if ctx(request).user and ctx(request).user.is_authenticated %}


app.state.templates = templates


# ---------------------------------------------------------
# 3. Middleware
# ---------------------------------------------------------
# Сессии
# Middleware для 401 → redirect
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret 123k;ld,nsdkjl"
)


app.add_middleware(AuthRedirectMiddleware)


# CORS (если понадобится)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ---------------------------------------------------------
# 4. Static files
# ---------------------------------------------------------
# app.mount( "/static", StaticFiles(directory="app/static"), name="static" )
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
log.info(f'Static BASE_DIR: {BASE_DIR}')
app.mount("/static", StaticFiles(directory=f'{BASE_DIR}/static'), name="static")

# ---------------------------------------------------------
# 5. Routers with prefixes & tags
# ---------------------------------------------------------
app.include_router(login_router)
app.include_router(api_router)

# app.include_router( login_router, prefix="/auth", tags=["Authentication"] )
# app.include_router( api_router, prefix="/api", tags=["IRR API"] )


# ---------------------------------------------------------
# 6. Error handlers
# ---------------------------------------------------------
@app.exception_handler(404)
def not_found(request: Request, exc):
    return templates.TemplateResponse(
        "errors/404.html",
        {"request": request},
        status_code=404
    )

@app.exception_handler(500)
def server_error(request: Request, exc):
    return templates.TemplateResponse(
        "errors/500.html",
        {"request": request},
        status_code=500
    )


# ---------------------------------------------------------
# 7. Root
# ---------------------------------------------------------
@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    return templates.TemplateResponse(
        "index.html",
        {"request": request}
    )
