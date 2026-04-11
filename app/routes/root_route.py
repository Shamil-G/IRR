from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse, HTMLResponse, FileResponse
from pathlib import Path

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context


router = APIRouter()


# -----------------------------
# 2. /about
# -----------------------------
@router.get("/about", response_class=HTMLResponse)
async def about(request: Request, ctx=Depends(template_context) ):
    return request.app.state.templates.TemplateResponse("about.html", { "request": request, **ctx, })


# -----------------------------
# 4. Корневая страница /
# -----------------------------
@router.get("/", response_class=HTMLResponse)
async def view_root(
    request: Request, user=Depends(login_required), ctx=Depends(template_context), ):
    return request.app.state.templates.TemplateResponse(
        "index.html", { "request": request, **ctx, }
    )


# -----------------------------
# 5. Установка языка
# -----------------------------
@router.get("/language/{lang}")
async def set_language(lang: str, request: Request):
    session = request.session

    log.debug(f"Set language ? {lang}, previous: {session.get('lang')}")
    session["lang"] = lang

    ref = request.headers.get("referer")
    log.debug(f"Set LANGUAGE. Referer: {ref}")

    return RedirectResponse(ref or "/")


# -----------------------------
# 6. Раздача файлов /uploads/*
# -----------------------------
@router.get("/uploads/{filename:path}")
async def uploaded_files(filename: str):
    file_path = Path("uploads") / filename
    return FileResponse(file_path)