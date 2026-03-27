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
def try_auto_login(request: Request):
    ip = ip_addr(request)
    req_json = {"ip_addr": ip}
    resp = requests.post(f"{sso_server}/check", json=req_json)

    log.info(f"LOGIN CHECK → {resp}")

    if resp.status_code != 200:
        return False

    resp_json = resp.json()
    log.info(f"LOGIN GET. resp_json: {resp_json}")

    if resp_json.get("status") != 200:
        log.info(f"Try auto login → USER {ip_addr(request)} not registered")
        return False

    json_user = resp_json["user"]
    log.info(f"LOGIN GET. json_user: {json_user}")

    # request.session["username"] = json_user["login_name"]

    user = SSO_User().authenticate_and_init(json_user, request)
    if not user:
        log.info("Try auto login → user object empty")
        request.state.user = None
        return False

    request.state.user = user

    log.info(f"SUCCESS. Try auto login → USER IP {ip}: {request.session}")
    return True


def login_required(request: Request):
    """
    Аналог Flask login_required.
    Берёт пользователя из request.session,
    создаёт SSO_User и кладёт в request.state.user.
    """

    session = request.session
    log.info(f'---> login_required')

    if "username" not in session or 'roles' not in session:
        log.info(f'---> login_required. USERNAME not in SESSION: {session}')
        status = try_auto_login(request)
        if not status:
            log.info(f'---> login_required. try_auto_login: {status}')
            raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)

    return request.state.user
