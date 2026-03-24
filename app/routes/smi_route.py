from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi import Query
from urllib.parse import urlencode

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.reports.report_smi_01 import report_01
from app.util.functions import get_regions
from app.models.smi_functions import get_rows, add, upd, set_action
from datetime import datetime

# FastAPI router
router = APIRouter()

# Заменитель login_required

@router.get("/print_smi", response_class=HTMLResponse, dependencies=[Depends(login_required)])
def view_print_smi(request: Request, ctx=Depends(template_context)):
    return request.app.state.templates.TemplateResponse("print_smi.html", {"request": request, **ctx})


@router.get('/print-smi/action')
def view_print_smi_action_get(
    request: Request,
    user=Depends(login_required),
    action: str = Query(...),
    prot_num: str = Query(...),
    event_date: str = Query(None),
    rfbn_id: str = Query(None),
    name: str = Query(None),
    smi_name: str = Query(None),
    description: str = Query(None),
):
    log.info(f'GET /print-smi/action. action: {action}, top_level: {user.top_level}')
    if action != "edit" or user.top_level>0:
        return RedirectResponse(url=request.url_for("print_smi_protocol"))

    params = {
        "prot_num": prot_num,
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "name": name,
        "smi_name": smi_name,
        "description": description,
    }
    clean_params = {k: v for k, v in params.items() if v is not None}
    log.info(f'GET /print-smi/action. clean_params: {clean_params}')
    return RedirectResponse( url=f"{request.url_for('print_smi_form')}?{urlencode(clean_params)}" )


@router.post('/print-smi/action')
def view_print_smi_action_post(
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
        'PRINT_SMI ACTION',
        'begin smi.set_action(:action, :prot_num, :top_level); end;',
        params
    )

    log.info(f'PRINT SMI ACTION POST → {params}')

    return RedirectResponse( url=request.url_for("print_smi_protocol"), status_code=303 )


@router.get('/print_smi/form', response_class=HTMLResponse, name="print_smi_form", dependencies=[Depends(login_required)])
async def view_form_print_smi_get(
    request: Request,
    ctx=Depends(template_context),

    prot_num: str | None = Query(None),
    event_date: str | None = Query(None),
    rfbn_id: str | None = Query(None),
    smi_name: str | None = Query(''),
    description: str | None = Query(''),
):
    # Собираем данные формы
    form = {
        "prot_num": prot_num,
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "smi_name": smi_name,
        "description": description,
    }

    log.info(f'VIEW FORM PRINT SMI (GET). data: {form}, ctx: {ctx}')

    # Преобразуем дату
    if event_date:
        try:
            form["event_date"] = datetime.strptime(event_date, "%Y-%m-%d").date()
        except:
            form["event_date"] = None

    return request.app.state.templates.TemplateResponse(
        "print_smi.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(ctx['user'].top_view, ctx['user'].rfbn_id),
            "message": "",
            **form,
            **ctx

        }
    )


@router.post('/print_smi/form', response_class=HTMLResponse, dependencies=[Depends(login_required)])
async def view_form_print_smi_post(
    request: Request,
    ctx=Depends(template_context),

    prot_num: str | None = Form(None),
    event_date: str = Form(...),
    rfbn_id: str = Form(...),
    smi_name: str = Form(...),
    description: str = Form(...),
):
    message=''
    form = {
        "event_date": event_date,
        "rfbn_id": rfbn_id,
        "smi_name": smi_name,
        "description": description,
        "employee": ctx['user'].fio,
    }

    if prot_num:
        # Редактирование
        form["prot_num"] = prot_num
        upd(form)
        return RedirectResponse( url=request.url_for("print_smi_protocol"), status_code=303 )

    log.info(f'POST FORM PRINT_SMI. data_post: {form}')
    # Новая запись
    add(form)
    message = "Информация успешно сохранена!"

    return request.app.state.templates.TemplateResponse(
        "print_smi.html",
        {
            "request": request,
            "active_tab": "form",
            "regions": get_regions(ctx['user'].top_view, ctx['user'].rfbn_id),
            "message": message,
            **form,   # ← ВАЖНО: возвращаем заполненные данные
            **ctx
        }
    )


@router.get( '/print_smi/protocol', 
            response_class=HTMLResponse, 
            dependencies=[Depends(login_required)], 
            name='print_smi_protocol')
async def view_print_smi_protocol_get(
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
        "print_smi.html",
        {
            "request": request,
            "active_tab": "protocol",
            "period": period,
            "list_protocols": rows,
            **ctx,
        }
    )
