from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Query
from urllib.parse import urlencode

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.reports.report_radio_01 import report_01
from app.util.functions import get_regions
from app.models.radio_functions import get_rows, add, set_action, upd
from datetime import datetime


# FastAPI router
router = APIRouter()


@router.get('/radio', response_class=HTMLResponse, dependencies=[Depends(login_required)])
def view_radio(request: Request, ctx=Depends(template_context)):
    return request.app.state.templates.TemplateResponse("radio.html", {"request": request, **ctx})


@router.get('/radio/report')
def radio_report(request: Request, user=Depends(login_required)):
    session = request.session
    if 'period' in session:
        params = {'rfbn_id': user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@router.get('/radio/action')
def view_radio_action_get(
    request: Request,
    user=Depends(login_required),

    action: str = Query(...),
    prot_num: str = Query(...),
    event_date: str = Query(None),
    rfbn_id: str = Query(None),
    channel_name: str = Query(''),
    speaker: str = Query(''),
    description: str = Query(''),
):
    if action != "edit" or user.top_level>0:
        log.info(f'RADIO ACTION. GET. Action: {action}, top_level: {user.top_level}')
        return RedirectResponse(url=request.url_for("radio_protocol"))

    params = {
        "prot_num": prot_num,
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "channel_name": channel_name,
        "speaker": speaker,
        "description": description,
    }
    clean_params = {k: v for k, v in params.items() if v is not None}
    log.info(f'RADIO ACTION. GET. Action: {action}, clean_params: {clean_params}')
    return RedirectResponse( url=f"{request.url_for('radio_form')}?{urlencode(clean_params)}" )


@router.post('/radio/action')
def view_radio_action_post(
    request: Request,
    action: str = Form(...),
    user=Depends(login_required),

    prot_num: str = Form(...),
):
    params = {
        "action": action,
        "prot_num": prot_num,
        "top_level": user.top_level,
    }
    # здесь action: approved, delete
    set_action(
        'RADIO ACTION',
        'begin radio.set_action(:action, :prot_num, :top_level); end;',
        params
    )

    log.info(f'RADIO ACTION. POST. PARAMS → {params}')

    return RedirectResponse(
        url=request.url_for("radio_protocol"),
        status_code=303
    )


@router.get('/radio/form', response_class=HTMLResponse, 
            name='radio_form')
def view_form_radio_get(    
    request: Request,
    user=Depends(login_required), 
    ctx=Depends(template_context),

    prot_num: str | None = Query(None),
    event_date: str | None = Query(None),
    rfbn_id: str | None = Query(None),

    channel_name: str = Query(''),
    speaker: str = Query(''),
    description: str = Query(''),
    ):
    message = ''
    form = {
        "prot_num": prot_num,
        "rfbn_id": rfbn_id,
        "channel_name": channel_name,
        "speaker": speaker,
        "description": description,
    }
    # Преобразуем дату
    if event_date:
        try:
            form["event_date"] = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            form["event_date"] = None

    return request.app.state.templates.TemplateResponse(
        "radio.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "top": user.top_level,
            "message": message,
            **form,
            **ctx
        }
    )


@router.post('/radio/form')
async def view_form_radio_post(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    prot_num: str | None = Form(None),
    event_date: str = Form(...),
    rfbn_id: str = Form(...),
    channel_name: str = Form(...),
    speaker: str = Form(...),
    description: str = Form(...),
    ):
    message=""
    form = { "event_date": event_date, "rfbn_id": rfbn_id,
             "channel_name": channel_name, "speaker": speaker, "description": description,
             "employee": user.fio
            }

    if prot_num:
        form["prot_num"] = prot_num
        upd(form)
        log.info(f'RADIO. UPDATE. FORM: {form}')
        # Обязательно Redirect чтобы считались все контексты
        return RedirectResponse( url=request.url_for("radio_protocol"), status_code=303 )

    log.info(f'--->RADIO_FORM. POST. \nADD DATA: {form}\n<---')
    add(form)
    message=f"Информация успешно сохранена!"
    
    return request.app.state.templates.TemplateResponse(
        "radio.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "message": message,
            **form,
            **ctx
        }
    )


@router.get('/radio/protocol', response_class=HTMLResponse, 
            dependencies=[Depends(login_required)], name='radio_protocol')
async def view_get_radio_protocol(
    request: Request,
    period: str | None = None,
    ctx=Depends(template_context),
):
    params ={}
    log.info(f'RADIO PROTOCOL. CHECK PERIOD. {period} : {request.session.get("period", "")}')
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
        log.info(f'RADIO. PROTOCOL. params: {params}')
        rows = get_rows(params)

    log.info(f'RADIO. PROTOCOL. GET PAGE. PERIOD: {period}')

    return request.app.state.templates.TemplateResponse(
        "radio.html",
        {
            "request": request,
            "active_tab": "protocol",
            "period": period,
            "list_protocols": rows,
            **ctx,
        }
    )

