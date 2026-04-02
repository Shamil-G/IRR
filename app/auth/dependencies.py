from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED

import requests

from app.auth.sso_user import SSO_User
from app.core.logger import log
from app.core.ip_addr import ip_addr
from app.config.app_config import sso_server

# -----------------------------
# 3. Авто‑логин через SSO /check
# -----------------------------
def check_login(request: Request):
    ip = ip_addr(request)
    req_json = {"ip_addr": ip}
    resp = requests.post(f"{sso_server}/check", json=req_json)

    log.info(f"LOGIN CHECK → {resp}")

    if resp.status_code != 200:
        return None

    resp_json = resp.json()
    log.info(f"LOGIN GET. resp_json: {resp_json}")

    if resp_json.get("status") != 200:
        log.info(f"Try auto login → USER {ip_addr(request)} not registered")
        return None
        
    json_user = resp_json["user"]
    log.info(f"LOGIN GET. json_user: {json_user}")
    return json_user


def try_auto_login(request: Request, json_user):
    user = SSO_User().authenticate_and_init(json_user, request)
    if not user:
        log.info("Try auto login → user object empty")
        request.state.user = None
        return False

    request.state.user = user

    log.info(f"SUCCESS. Try auto login → USER IP {ip}: {request.session}")
    return True


def login_required(request: Request):

    json_user = check_login(request)
    if not json_user:
        log.info(f'---> login_required. user out of session')
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    session = request.session

    if "username" not in session or 'roles' not in session:
        log.info(f'---> login_required. USERNAME not in SESSION: {session}')
        status = try_auto_login(request)
        if not status:
            log.info(f'---> login_required. try_auto_login: {status}')
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    user = SSO_User().restore_user(request)
    if not user:
        raise HTTPException(HTTP_401_UNAUTHORIZED)

    request.state.user = user
    return request.state.user

