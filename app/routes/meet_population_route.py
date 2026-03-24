from fastapi import APIRouter, UploadFile, Request, Depends, Form, File, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND
import json
from typing import List
from datetime import datetime, date

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.util.functions import get_regions, upload_files, extract_payload

from app.models.irr_functions import get_list_rayons, get_partners, add_protocol, update_protocol, get_rows, set_action, get_org_name
from app.routes.common_route import get_cached_rayons, category_to_english


# FastAPI router
router = APIRouter()


# GET
@router.get('/meet_population/form',  name='meet_population_form')
def view_form_meet_population_get(
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
    meeting_place: str | None = Query(''),
    path_photo: str | None = Query(None),    # JSON string
):
    form = {
        "prot_num": prot_num,
        "rfbn_id": rfbn_id or user.rfbn_id,
        "district": district,
        "cnt_total": cnt_total,
        "cnt_women": cnt_women,
        "speaker": speaker,
        "meeting_format": meeting_format,
        "meeting_place": meeting_place,
    }
    if date_irr:
        try:
            form['date_irr'] = datetime.strptime(date_irr, "%Y-%m-%d").date()
        except:
            form['date_irr'] = None
    else:
        form['date_irr'] = date.today()

    if partners:
        try:
            form['partners'] = json.loads(form['partners'])
        except:
            form['partners'] = get_partners()

    if path_photo:
        try:
            form['path_photo'] = json.loads(form['path_photo'])
        except:
            form['path_photo'] = []

    log.info(f'MEET LABOR. GET. data: {form}')

    return request.app.state.templates.TemplateResponse(
        'meet.html',
        {
        "request": request,
        "active_tab": "form_population",
        "regions": get_regions(user.top_view, user.rfbn_id),
        "districts": get_cached_rayons(user.rfbn_id),
        "list_partners": get_partners(),
        "message": '',
        **form,
        **ctx
        }
    )


# POST
@router.post('/meet_population/form')
async def view_form_meet_population_post(
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
    meeting_place: str = Form(...),
    path_photo: List[UploadFile] = File([]),
):
    message = ""

    # -----------------------------
    # 1. ВАЛИДАЦИЯ
    # -----------------------------
    if len(partners) < 1:
        message += "Необходимо выбрать не менее чем одну организацию-партнера. "

    if not bin and not organization_name:
        message += "Необходимо выбрать БИН организации. "

    real_photos = [p for p in path_photo if p.filename]
    if not prot_num and not real_photos:
        message += "Необходимо выбрать не менее 1 файла."

    # -----------------------------
    # 2. Ошибки → вернуть форму
    # -----------------------------
    if message:
        try:
            date_irr_date = datetime.strptime(date_irr, "%Y-%m-%d").date()
        except:
            date_irr_date = None

        return request.app.state.templates.TemplateResponse(
            'meet.html',
            {
                "request": request,
                "active_tab": "form_population",
                "regions": get_regions(user.top_view, user.rfbn_id),
                "districts": get_cached_rayons(user.rfbn_id),
                "message": message,
                "list_partners": get_partners(),

                # Возвращаем данные формы
                "prot_num": prot_num,
                "date_irr": date_irr_date,
                "rfbn_id": rfbn_id,
                "district": district,
                "cnt_total": cnt_total,
                "cnt_women": cnt_women,
                "speaker": speaker,
                "meeting_format": meeting_format,
                "meeting_place": meeting_place,
                "partners": partners,
                **ctx
            }
        )

    # -----------------------------
    # 3. Подготовка данных
    # -----------------------------
    try:
        date_irr_date = datetime.strptime(date_irr, "%Y-%m-%d").date()
    except:
        date_irr_date = None

    partners_json = json.dumps(partners, ensure_ascii=False)

    photo_names = []
    if real_photos:
        photo_names = upload_files(rfbn_id, real_photos)

    path_photo_json = json.dumps(photo_names, ensure_ascii=False)

    db_data = {
        "date_irr": date_irr_date,
        "rfbn_id": rfbn_id,
        "district": district,
        "cnt_total": cnt_total,
        "cnt_women": cnt_women,
        "speaker": speaker,
        "meeting_format": meeting_format,
        "partners": partners_json,
        "meeting_place": meeting_place,
        "path_photo": path_photo_json,
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
        f"/meet_population/form?"
        f"prot_num=&"
        f"date_irr={date_irr}&"
        f"rfbn_id={rfbn_id}&"
        f"district={district}&"
        f"cnt_total={cnt_total}&"
        f"cnt_women={cnt_women}&"
        f"speaker={speaker}&"
        f"meeting_format={meeting_format}&"
        f"partners={partners_json}&"
        f"meeting_place={meeting_place}&"
        f"path_photo={path_photo_json}"
    )

    return RedirectResponse(url=url, status_code=303)
