from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Query
from urllib.parse import urlencode

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.reports.report_round_table_01 import report_01
from app.util.functions import get_regions
from app.models.round_table_functions import get_rows, add, set_action, upd
from datetime import datetime


# FastAPI router
router = APIRouter()


@router.get('/round_table', response_class=HTMLResponse, dependencies=[Depends(login_required)])
def view_round_table(request: Request, ctx=Depends(template_context)):
    return request.app.state.templates.TemplateResponse("round_table.html", {"request": request, **ctx})


@router.get('/round-table/report')
def round_table_report(request: Request, user=Depends(login_required)):
    session = request.session
    if 'period' in session:
        params = {'rfbn_id': user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''


@router.get('/round_table/action')
def view_print_smi_action_get(
    request: Request,
    user=Depends(login_required),
    action: str = Query(...),

    prot_num: str = Query(...),
    event_date: str = Query(None),
    rfbn_id: str = Query(None),
    participants: str = Query(None),
    refer: str = Query(None),
    description: str = Query(None),
):
    log.info(f'GET /print-smi/action. action: {action}, top_level: {user.top_level}')
    if action != "edit" or user.top_level>0:
        return RedirectResponse(url=request.url_for("round_table_protocol"))

    params = {
        "prot_num": prot_num,
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "refer": refer,
        "description": description,
    }
    clean_params = {k: v for k, v in params.items() if v is not None}
    log.info(f'GET /print-smi/action. clean_params: {clean_params}')
    return RedirectResponse( url=f"{request.url_for('round_table_form')}?{urlencode(clean_params)}" )


@router.post('/round_table/action')
def view_round_table_action_post(
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
    set_action(
        'ROUNDTABLE ACTION',
        'begin round_table.set_action(:action, :prot_num, :top_level); end;',
        params
    )

    log.info(f'ROUND TABLE ACTION POST → {params}')

    return RedirectResponse(
        url=request.url_for("round_table_protocol"),
        status_code=303
    )


@router.get('/round_table/form', response_class=HTMLResponse, 
            name="round_table_form")
async def view_form_print_smi_get(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    prot_num: str | None = Query(None),
    event_date: str | None = Query(None),
    rfbn_id: str | None = Query(None),
    participants: str | None = Query(''),
    refer: str | None = Query(''),
    description: str | None = Query(''),
):
    # Собираем данные формы
    form = {
        "prot_num": prot_num,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "refer": refer,
        "description": description,
    }

    log.info(f'VIEW FORM ROUND TABLE (GET). data: {form}')

    # Преобразуем дату
    if event_date:
        try:
            form["event_date"] = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            form["event_date"] = None

    return request.app.state.templates.TemplateResponse(
        "round_table.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "top": user.top_level,
            "message": "",
            **form,
            **ctx,
        }
    )


@router.post('/round_table/form', response_class=HTMLResponse)
async def view_form_round_table_post(
    request: Request,
    user=Depends(login_required),
    ctx=Depends(template_context),

    prot_num: str | None = Form(None),
    event_date: str = Form(...),
    rfbn_id: str = Form(...),
    participants: str = Form(...),
    refer: str = Form(...),
    description: str = Form(...),
):
    message=''
    form = {
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "participants": participants,
        "refer": refer,
        "description": description,
        "employee": user.fio,
    }

    if prot_num:
        # Редактирование
        form["prot_num"] = prot_num
        upd(form)
        return RedirectResponse( url=request.url_for("round_table_protocol"), status_code=303 )

    log.info(f'POST FORM ROUND TABLE. data_post: {form}')
    # Новая запись
    add(form)
    message = "Информация успешно сохранена!"

    return request.app.state.templates.TemplateResponse(
        "print_smi.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(user.top_view, user.rfbn_id),
            "top": user.top_level,
            "message": message,
            **form,   # ← ВАЖНО: возвращаем заполненные данные
            **ctx,
        }
    )


@router.get('/round_table/protocol', response_class=HTMLResponse, 
            dependencies=[Depends(login_required)], 
            name='round_table_protocol')
async def view_get_round_table_protocol(
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
        "round_table.html",
        {
            "request": request,
            "active_tab": "protocol",
            "period": period,
            "list_protocols": rows,
            **ctx,
        }
    )

