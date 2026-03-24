#from fastapi.responses import TemplateResponse
from starlette.status import HTTP_401_UNAUTHORIZED
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import RedirectResponse
from starlette.templating import _TemplateResponse

from fastapi import Request
from app.core.i18n import get_i18n_value
from app.util.functions import get_flashed_messages
from app.core.logger import log
from app.config.app_config import styles


def get_lang(request: Request) -> str:
    return request.session.get("language", "ru")

# -----------------------------
# 1. Аналог context_processor
# -----------------------------
def template_context(request: Request):
    session = request.session

    if "style" not in session:
        session["style"] = styles[0]
    if "lang" not in session:
        session["lang"] = "ru"

    return {
        "user": getattr(request.state, "user", None),
        "style": session.get("style"),
        "lang": session.get("lang"),
        "top_view": session.get("top_view"),
        "top_level": session.get("top_level"),
    }


# -----------------------------
# 2. Middleware: аналог after_request
# -----------------------------
class AuthRedirectMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # API и login/logout пропускаем без обработки
        if (
            request.url.path in ("/login", "/logout")
            or request.url.path.startswith("/api")
        ):
            return await call_next(request)

        response = await call_next(request)

        if response.status_code == HTTP_401_UNAUTHORIZED:
            return RedirectResponse(url="/login")

        return response
