from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse

from app.auth.dependencies import login_required
from app.core.logger import log
from functools import lru_cache
from datetime import datetime
from app.core.logger import log
from app.util.regions import regions
from app.util.functions import upload_files, extract_payload
from app.auth.dependencies import login_required

from app.models.irr_functions import (
    get_org_name,
    get_list_rayons,
    load_protocol,
    get_partners,
    update_protocol,
)
from app.auth.sso_user import SSO_User
import json

router = APIRouter()


# -----------------------------
# 1. API: /api/organization/
# -----------------------------
@router.post("/api/organization/", response_class=JSONResponse)
async def view_organization_name(request: Request, user=login_required):
    data = await extract_payload(request)
    log.info(f"API_ORGANIZATION: {data}")
    return get_org_name(data)


# -----------------------------
# 2. Кэш районов
# -----------------------------
@lru_cache(maxsize=32)
def get_cached_rayons(rfbn_id: str):
    rayons = get_list_rayons(rfbn_id) or []
    log.info(f"GET CACHED RAYONS for {rfbn_id}: {rayons}")
    return {item["rfbn_id"]: item["name"] for item in rayons}


# -----------------------------
# 3. Категория → английский
# -----------------------------
def category_to_english(nm: str) -> str:
    match nm:
        case "большой":
            return "large"
        case "средний":
            return "middle"
        case "малый":
            return "small"
        case _:
            return nm


# -----------------------------
# 4. /edit-protocol/<prot_num>
# -----------------------------
@router.api_route("/edit-protocol/{prot_num}", methods=["GET", "POST"], response_class=HTMLResponse)
async def protocol_form(
    prot_num: str,
    request: Request,
    user =  Depends(login_required),
):
    session = request.session
    list_partners = get_partners()
    message = ""
    load_data = {}

    # -----------------------------
    # Доступные регионы
    # -----------------------------
    if user.top_level == 0:
        list_regions = {user.rfbn_id: regions[user.rfbn_id]}
    else:
        list_regions = regions

    list_rayons = get_cached_rayons(user.rfbn_id)

    # -----------------------------
    # GET → загрузка протокола
    # -----------------------------
    if request.method == "GET":
        load_data = load_protocol(prot_num)

        ctx = {
            "request": request,
            "data": load_data,
            "regions": list_regions,
            "districts": list_rayons,
            "top": user.top_level,
            "message": "",
            "list_partners": list_partners,
        }
        return request.app.state.templates.TemplateResponse("edit_protocol.html", ctx)

    # -----------------------------
    # POST → обработка формы
    # -----------------------------
    form = await request.form()
    files = await request.form()

    load_data = dict(form)

    rfbn_id = load_data.get("rfbn_id", "")
    meeting_place = load_data.get("meeting_place", "")
    bin_value = load_data.get("bin", "")
    partners = form.getlist("partners")
    photos = request.files.getlist("path_photo")

    # -----------------------------
    # Валидация
    # -----------------------------
    if len(partners) < 1:
        message += "Необходимо выбрать не менее чем одну организацию. "

    if len(meeting_place) == 0 and len(bin_value) == 0:
        message += "Необходимо выбрать либо адрес проведения ИРР, либо организацию. "

    if not any(f.filename for f in photos):
        message += "Необходимо выбрать не менее 1 файла."

    if message:
        load_data["partners"] = partners
        load_data["date_irr"] = datetime.strptime(load_data["date_irr"], "%Y-%m-%d").date()

        ctx = {
            "request": request,
            "data": load_data,
            "regions": list_regions,
            "districts": list_rayons,
            "top": user.top_level,
            "message": message,
            "list_partners": list_partners,
        }
        return request.app.state.templates.TemplateResponse("edit_protocol.html", ctx)

    # -----------------------------
    # Сохранение файлов
    # -----------------------------
    list_path = await upload_files(rfbn_id, photos)

    load_data["path_photo"] = json.dumps(list_path, ensure_ascii=False)
    load_data["partners"] = json.dumps(partners, ensure_ascii=False)
    load_data["employee"] = user.fio
    load_data["prot_num"] = prot_num

    log.info(f"EDIT PROTOCOL. POST. Files: {list_path}")

    update_protocol(load_data)

    return RedirectResponse("/list-protocols", status_code=302)
