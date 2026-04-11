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

def fetch_user_from_sso(endpoint: str, req_json: dict) -> SSO_User | None:
    resp = requests.post(url=f'{sso_server}/{endpoint}', json=req_json)
    if resp.status_code != 200:
        return None
    resp_json = resp.json()
    status = resp_json.get("status")
    if status != 200:
            match status:
                case 202: log.info(f"--->\nERROR CHECK LOGIN. Session time is out, status {status}\n<---")
                case _:   log.info(f"--->\nERROR CHECK LOGIN. STATUS {status}\n<---")
            return None

    if resp_json.get('status') == 200 and 'user' in resp_json:
        return resp_json['user']
    return None


def try_auto_login(request):
    ip = ip_addr(request)
    req_json = {"ip_addr": ip}
    if ip == "127.0.0.1" and "login_name" in request.session:
        req_json["login_name"] = request.session.get("login_name", "")

    json_user = fetch_user_from_sso("check", req_json)
    if not json_user:
        log.info(f"---\nTRY AUTO LOGIN. FAIL JSON USER. REQ_JSON{req_json}\n---")
        return False

    user = SSO_User().authenticate_and_init(json_user, request)

    if not user:
        log.info(f"---\nTRY AUTO LOGIN. FAIL. {json_user}\n---")
        request.state.user = None
        return False

    request.state.user = user

    log.debug(f"---\nTRY AUTO LOGIN. SUCCESS. {json_user}")
    return True


# def check_login(request: Request):
#     return try_auto_login(request)


def login_required(request: Request):

    status = try_auto_login(request)
    if not status:
        log.info(f'---> login_required. user out of session')
        raise HTTPException(status_code=HTTP_401_UNAUTHORIZED)
    return request.state.user

