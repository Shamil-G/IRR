from fastapi import APIRouter, UploadFile, Request, Depends, Form, File, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND
import json
from typing import List
from datetime import datetime, date
from urllib.parse import quote, unquote

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.util.functions import get_regions, upload_files

from app.models.irr_functions import get_list_rayons, get_partners, add_protocol, update_protocol, get_rows, set_action, get_org_name
from app.routes.common_route import get_cached_rayons, category_to_english



# FastAPI router
router = APIRouter()


# GET
@router.get('/meet_labor/form', name='meet_labor_form')
def view_form_meet_labor_get(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    # GET параметры с URL
    prot_num: str | None = Query(None),
    date_irr: str | None = Query(None),
    rfbn_id: str | None = Query(None),
    district: str | None = Query(''),
    cnt_total: int | None = Query(None),
    cnt_women: int | None = Query(None),
    speaker: str | None = Query(''),
    meeting_format: str | None = Query(''),
    partners: str | None = Query(None),      # JSON string
    category: str | None = Query(''),
    bin: str | None = Query(''),
    organization_name: str | None = Query(None),
    path_photo: str | None = Query(None),    # JSON string
):
    form = {
        "prot_num": prot_num,
        "date_irr": date_irr or date.today(),
        "rfbn_id": rfbn_id or user.rfbn_id,
        "district": district,
        "cnt_total": cnt_total,
        "cnt_women": cnt_women,
        "speaker": speaker,
        "meeting_format": meeting_format,
        "category": category,
        "bin": bin,
        "organization_name": organization_name,
    }
    if partners:
        try:
            form["partners"] = json.loads(unquote(partners))
        except Exception as e:
            log.error(f"PARTNERS PARSE ERROR: {e}")
            form["partners"] = []
    else:
        form["partners"] = []

    log.debug(f'MEET LABOR. GET. data: {form}')

    return request.app.state.templates.TemplateResponse(
        'meet.html',
        {
        "request": request,
        "active_tab": "form_labor",
        "regions": get_regions(user.top_view, user.rfbn_id),
        "districts": get_cached_rayons(user.rfbn_id),
        "list_partners": get_partners(),
        "message": '',
        **form,
        **ctx
        }
    )

#################################
# POST
#################################
@router.post('/meet_labor/form')
async def view_form_meet_labor_post(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    prot_num: str | None = Form(None),
    date_irr: str = Form(...),
    rfbn_id: str = Form(...),
    district: str = Form(...),
    cnt_total: int = Form(...),
    cnt_women: int = Form(...),
    speaker: str = Form(...),
    meeting_format: str = Form(...),
    partners: List[str] = Form(...),
    category: str = Form(...),
    bin: str = Form(...),
    organization_name: str = Form(""),
    path_photo: List[UploadFile] = File([]),
):
    message = ""
    real_name_photos = [p for p in path_photo if p.filename]
    # -----------------------------
    # 1. ВАЛИДАЦИЯ только для новых
    # -----------------------------
    if not prot_num:
        if len(partners) < 1:
            message += "Необходимо выбрать не менее чем одну организацию-партнера. "

        if not bin or not organization_name:
            message += "Необходимо выбрать БИН организации. "

        if not real_name_photos:
            message += "Необходимо выбрать не менее 1 файла."

    # -----------------------------
    # 2. Ошибки → вернуть форму
    # -----------------------------
    if message:
        return request.app.state.templates.TemplateResponse(
            'meet.html',
            {
                "request": request,
                "active_tab": "form_labor",
                "regions": get_regions(user.top_view, user.rfbn_id),
                "districts": get_cached_rayons(user.rfbn_id),
                "message": message,
                "list_partners": get_partners(),

                # Возвращаем данные формы
                "prot_num": prot_num,
                "date_irr": date_irr,
                "rfbn_id": rfbn_id,
                "district": district,
                "cnt_total": cnt_total,
                "cnt_women": cnt_women,
                "speaker": speaker,
                "meeting_format": meeting_format,
                "category": category,
                "bin": bin,
                "organization_name": organization_name,
                "partners": partners,
                **ctx
            }
        )

    # -----------------------------
    # 3. Подготовка данных
    # -----------------------------
    partners_json = json.dumps(partners, ensure_ascii=False)
    # Для сохранения на форме 
    partners_encoded = quote(partners_json)   

    photo_names = []
    if real_name_photos:
        photo_names = await upload_files(rfbn_id, real_name_photos)

    path_photo_json = json.dumps(photo_names, ensure_ascii=False)

    db_data = {
        "date_irr": date_irr,
        "rfbn_id": rfbn_id,
        "district": district,
        "cnt_total": cnt_total,
        "cnt_women": cnt_women,
        "speaker": speaker,
        "meeting_format": meeting_format,
        "partners": partners_json,
        "category": category,
        "bin": bin,
        "organization_name": organization_name,
        "path_photo": path_photo_json if len(real_name_photos)>0 else None,
        "employee": user.fio,
    }

    # -----------------------------
    # 4. INSERT или UPDATE
    # -----------------------------
    if prot_num:
        db_data["prot_num"] = prot_num
        update_protocol(db_data)
        return RedirectResponse("/meet/protocol", status_code=303)

    add_protocol(db_data)

    # -----------------------------
    # 5. РЕДИРЕКТ           
    # -----------------------------
    # Создание → остаёмся в форме (PRG)
    url = (
        f"/meet_labor/form?"
        f"date_irr={date_irr}&"
        f"rfbn_id={rfbn_id}&"
        f"district={district}&"
        f"speaker={speaker}&"
        f"meeting_format={meeting_format}&"
        f"partners={partners_encoded}"
    )
    log.debug(f'LABOR ROUTE. POST. URL: {url}')
    return RedirectResponse(url=url, status_code=303)
