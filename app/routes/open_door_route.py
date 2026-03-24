from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Query
from urllib.parse import urlencode

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.reports.report_open_door_01 import report_01
from app.util.functions import get_regions
from app.models.open_door_functions import get_rows, add, upd, set_action
from datetime import datetime


# FastAPI router
router = APIRouter()


@router.get('/open_door', response_class=HTMLResponse, dependencies=[Depends(login_required)])
def view_open_door(request: Request, ctx=Depends(template_context)):
    return request.app.state.templates.TemplateResponse("open_door.html", {"request": request, **ctx })


@router.get('/open-door/report')
def open_door_report(request: Request, user=Depends(login_required)):
    session = request.session
    if 'period' in session:
        params = {'rfbn_id': user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@router.get('/open-door/action')
def view_open_door_action_get(
    request: Request,
    user=Depends(login_required),

    action: str = Query(...),
    prot_num: str = Query(...),
    event_date: str = Query(None),
    rfbn_id: str = Query(None),
    participants: str = Query(None),
    smi: str = Query(None),
    event_place:  str = Query(None),
    refer:  str = Query(None)
):
    log.info(f'GET /open_door/action. action: {action}, top_level: {user.top_level}')
    if action != "edit" or user.top_level>0:
        return RedirectResponse(url=request.url_for("open_door_protocol"))

    params = {
        "prot_num": prot_num,
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "smi": smi,
        "event_place": event_place,
        "refer": refer
    }
    clean_params = {k: v for k, v in params.items() if v is not None}
    log.info(f'GET /open_door/action. clean_params: {clean_params}')
    return RedirectResponse( url=f"{request.url_for('open_door_form')}?{urlencode(clean_params)}" )


@router.post('/open_door/action')
def view_open_door_action_post(
    request: Request,
    user=Depends(login_required),
    action: str = Form(...),
    prot_num: str = Form(...),
):
    params = {
        "action": action,
        "prot_num": prot_num,
        "top_level": user.top_level,
    }
    # здесь action: approved, delete
    set_action( 'OPEN DOOR', 'begin open_door.set_action(:action, :prot_num, :top_level); end;', params )

    log.info(f'OPEN DOOR ACTION POST → {params}')

    return RedirectResponse( url=request.url_for("open_door_protocol"), status_code=303 )


@router.get('/open_door/form', response_class=HTMLResponse, name="open_door_form")
async def view_form_open_door_get(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    prot_num: str | None = Query(None),
    event_date: str | None = Query(None),
    rfbn_id: str | None = Query(None),
    participants: str | None = Query(''),
    smi: str | None = Query(''),
    event_place: str | None = Query(''),
    refer: str | None = Query(''),
):
    # Собираем данные формы
    form = {
        "prot_num": prot_num,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "smi": smi,
        "event_place": event_place,
        "refer": refer
    }

    log.info(f'VIEW OPEN DOOR TABLE (GET). data: {form}')

    # Преобразуем дату
    if event_date:
        try:
            form["event_date"] = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            form["event_date"] = None

    return request.app.state.templates.TemplateResponse(
        "open_door.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "top": user.top_level,
            "message": "",
            **form,
            **ctx
        }
    )


@router.post('/open_door/form', response_class=HTMLResponse)
async def view_form_open_door_post(
    request: Request,
    user=Depends(login_required),

    prot_num: str | None = Form(None),
    event_date: str = Form(...),
    rfbn_id: str = Form(...),

    participants: str = Form(...),
    smi: str = Form(...),
    event_place: str = Form(...),
    refer: str = Form(...),
):
    message=''
    form = {
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "smi": smi,
        "event_place": event_place,
        "refer": refer,
        "employee": user.fio,
    }

    if prot_num:
        # Новая запись
        add(form)
        message = "Информация успешно сохранена!"
        log.info(f'POST FORM OPEN DOOR. ADD: {form}')

    if prot_num:
        # Редактирование
        form["prot_num"] = prot_num
        upd(form)
        log.info(f'POST FORM OPEN DOOR. UPDATE: {form}')
        return RedirectResponse( url=request.url_for("open_door_protocol"), status_code=303 )

    return request.app.state.templates.TemplateResponse(
        "open_door.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "top": user.top_level,
            "message": message,
            **form,   # ← ВАЖНО: возвращаем заполненные данные
            "user": user
        }
    )


@router.get('/open_door/protocol', response_class=HTMLResponse, 
            dependencies=[Depends(login_required)], name='open_door_protocol')
async def view_get_open_door_protocol(
    request: Request,
    period: str | None = None,
    ctx=Depends(template_context),
):
    if period:
        request.session["period"] = period
    else:
        period = request.session.get("period", "")

    rows = []
    if period:
        params = {
            'rfbn_id': request.state.user.rfbn_id[:2],
            'top_view': request.state.user.top_view,
            'period': period,
        }
        rows = get_rows(params)

    return request.app.state.templates.TemplateResponse(
        "open_door.html",
        {
            "request": request,
            "active_tab": "protocol",
            "period": period,
            "list_protocols": rows,
            **ctx,
        }
    )
