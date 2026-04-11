from fastapi import APIRouter, Request, Depends, status
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Form

import requests
import os

from app.auth.sso_user import SSO_User
from app.auth.dependencies import login_required
from app.core.logger import log
from app.config.app_config import sso_server, styles
from app.core.ip_addr import ip_addr
from app.core.inject_template import template_context, get_lang


router = APIRouter()


# -----------------------------
# 1. Аналог Flask logout
# -----------------------------
@router.get("/logout")
async def logout(request: Request):
    ip = ip_addr(request)
    req_json = {"ip_addr": ip}

    session = request.session
    
    log.info(f'*** logout session')
    if 'login_name' in session:
        req_json["login_name"] = session.get('login_name')
        log.info( f"---\nLOGOUT req_json: {req_json}\n---")

    # Очистка данных сессии (если используешь starlette session middleware)
    if "username" in request.session:
        request.session.pop("username")
    if "password" in request.session:
        request.session.pop("password")
    if "info" in request.session:
        request.session.pop("info")

    # Уведомляем SSO‑сервер
    resp = requests.post(f"{sso_server}/close", json=req_json)

    if resp.status_code != 200:
        return RedirectResponse(url="/")

    resp_json = resp.json()

    if resp_json.get("status") != 200:
        log.info(
            f"LOGOUT ERROR: ошибка закрытия сессии. "
            f"Статус: {resp_json.get('status')} / {ip}"
        )

    return RedirectResponse(url=request.url_for("login"), status_code=status.HTTP_302_FOUND)

# -----------------------------
# 3. Подключение middleware в main.py
# -----------------------------
# В main.py:
#
# from auth.user_login_sso import auth_redirect_middleware
# app.middleware("http")(auth_redirect_middleware)
#
# -----------------------------
@router.get("/login", name="login")
async def login_page(request: Request, ctx=Depends(template_context) ):
    log.info(f'LOGIN. GET. CTX: {ctx}')

    return request.app.state.templates.TemplateResponse(
        "login.html",
        { "request": request, **ctx }
    )

@router.post("/login")
async def login_submit(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    ctx=Depends(template_context)
):
    req_json = {
        "login_name": username,
        "password": password,
        "ip_addr": ip_addr(request),
    }

    log.info(f"LOGIN_PAGE. POST. REQUEST JSON: {req_json}")

    resp = requests.post(f"{sso_server}/login", json=req_json)
    
    # Проверяем наличие сетевой ошибки
    if resp.status_code != 200:
        log.info(
            f"LOGIN_PAGE. Ошибка {resp.status_code} соединения с SSO"
        )
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {
                "request": request, 
                "user": None,
                "info": "Ошибка {resp.status_code} соединения с SSO",
                **ctx
            }
        )
    # Связь проверили - теперь проверим а получили ли мы запрашиваемый объект для регистрации
    resp_json = resp.json()
    if resp_json.get("status") != 200:
        log.info(
            f"LOGIN_PAGE. POST. USER {username} not registered"
        )
        return request.app.state.templates.TemplateResponse(
            "login.html",
            {"request": request, 
             "user": None,
             "info": "Неверна Фамилия (или ИИН) или пароль",
             **ctx,
             'username': username
            },
        )

    # JSON получили
    json_user = resp_json["user"]
    log.debug(f"LOGIN POST. json_user: {json_user}")
   
    # -----------------------------
    # Создание SSO_User
    # -----------------------------
    if json_user:
        # log.info(f"LOGIN. json_user: {json_user}")
        # Проверяем роли и кладем их в сессию
        user = SSO_User().authenticate_and_init(json_user, request)
        
        # Если роль таки не дана то user == None
        if not user:
            log.info(
                "LOGIN_PAGE. ERROR LOGIN. User object empty. "
                "DEP_NAME not permitted? May be Post not permitted?"
            )
            return request.app.state.templates.TemplateResponse(
                "login.html", 
                {"request": request, 
                 "user": None,
                 "info": "Неверна Фамилия (или ИИН) или пароль",
                 **ctx,
                'username': username
                },
            )
        
        # Пока не знаю для чего эта строка
        request.state.user = user
        # -----------------------------
        # Редирект на next или /
        # -----------------------------
        next_page = request.query_params.get("next")
        if next_page:
            log.info(f"LOGIN_PAGE. SUCCESS. GOTO NEXT PAGE: {next_page}")
            return RedirectResponse(url=next_page, status_code=303)

        log.info(f"LOGIN_PAGE. SUCCESS\nSESSION: {request.session}\nGOTO NEXT ROOT")
        return RedirectResponse(url="/", status_code=302)
