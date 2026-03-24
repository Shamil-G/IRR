from fastapi import FastAPI
from starlette.middleware.sessions import SessionMiddleware
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from app.core.inject_template import AuthRedirectMiddleware, template_context
from app.auth.login_routes import router as login_router
from app.routes import router as api_router
from app.core.i18n import get_i18n_value

from jinja2 import pass_context

@pass_context
def res_value(ctx, key):
    request = ctx["request"]
    lang = request.session.get("lang", "ru")
    return get_i18n_value(lang, key)


app = FastAPI()

######################
# Begin Jinja2 Section
######################

templates = Jinja2Templates(directory="app/templates")

templates.env.globals["res_value"] = res_value

# templates.env.globals["ctx"] = template_context
# Example:
# {% if ctx(request).user and ctx(request).user.is_authenticated %}

app.state.templates = templates
####################
# End Jinja2 Section
####################

# Сессии
# Middleware для 401 → redirect
app.add_middleware(
    SessionMiddleware,
    secret_key="super-secret 123k;ld,nsdkjl"
)
app.add_middleware(AuthRedirectMiddleware)

#static
app.mount( "/static", StaticFiles(directory="app/static"), name="static" )

# Подключаем SSO‑роуты
app.include_router(login_router)
app.include_router(api_router)

#print(app.routes)

