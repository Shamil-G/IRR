from fastapi import APIRouter, UploadFile, Request, Depends, Form, File, Query
from fastapi.responses import RedirectResponse, HTMLResponse
from starlette.status import HTTP_302_FOUND
from urllib.parse import urlencode
import json
from typing import List
from datetime import datetime

from app.auth.dependencies import login_required
from app.core.logger import log
from app.core.inject_template import template_context
from app.util.functions import get_regions, upload_files, extract_payload

from app.models.irr_functions import get_list_rayons, get_partners, add_protocol, update_protocol, get_rows, set_action, get_org_name
from app.routes.common_route import get_cached_rayons, category_to_english
from app.reports.report_meet_01 import report_01

# FastAPI router
router = APIRouter()

## Выбираем сам протокол
@router.get('/meeting', dependencies=[Depends(login_required)])
def view_meeting(request: Request, ctx=Depends(template_context)):
    return request.app.state.templates.TemplateResponse("meet.html", {"request": request, **ctx})


@router.get('/meet/report')
def meet_report(request: Request, user=Depends(login_required)):
    session = request.session
    if 'period' in session:
        params = {'rfbn_id': user.rfbn_id[0:2], 'period': session['period']}
        return report_01(params)
    return ''



@router.api_route('/meet/action', methods=['GET','POST'])
async def view_protocol_action(request: Request, user=Depends(login_required)):
    data = await extract_payload(request)

    if data.get('action')=='edit':
        base = request.url_for(f"meet_{data.get('page')}_form")
        query = urlencode(data)
        log.debug(f'--->\nMEET ACTION. POPULATION. query: {query}\n<---')
        return RedirectResponse(f"{base}?{query}", status_code=302)

    args = {'action': data['action'], 'prot_num': data['prot_num'], 'top_level': user.top_level}
    set_action('VIEW ACTION', 'begin manage.set_action(:action, :prot_num, :top_level); end;', args);

    return RedirectResponse(
        url=request.url_for("meet_protocol"),
        status_code=HTTP_302_FOUND
    )


@router.get('/meet/protocol', response_class=HTMLResponse, 
            dependencies=[Depends(login_required)], name='meet_protocol')
async def view_get_meet_protocol(
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
    log.info(f'MEET_PROTOCOL. \nperiod: {period}\nrows: {rows}')
    return request.app.state.templates.TemplateResponse(
        "meet.html",
        {
            "request": request,
            "active_tab": "protocol",
            "period": period,
            "rows": rows,
            **ctx,
        }
    )

# @router.get('/meet/protocol', response_class=HTMLResponse, name='meet_protocol')
# async def view_meet_protocol_get(
#         request: Request, 
#         period: str | None = None,
#         user=Depends(login_required), 
#         ctx=Depends(template_context), 
#         ):
#     if period:
#         request.session["period"] = period
#     else:
#         period = request.session.get("period", "")

#     return request.app.state.templates.TemplateResponse(
#         "meet.html", { "request": request, **ctx, "active_tab": "protocol", "period": period,  }
#     )


# @router.post('/meet/protocol')
# def view_meet_protocol_post( request: Request,  user=Depends(login_required),  
#                              ctx=Depends(template_context), period: str = Form(...)  ):
#     session = request.session
#     session['period'] = period

#     params = {'rfbn_id': user.rfbn_id[0:2], 'top_view': user.top_view, 'period': period} 
#     rows = list_protocol(params)

#     # if len(rows)==0:
#     #     render_template('meet.html', data=rows, level=user.top_level)

#     if user.top_view==0:
#         list_regions = { user.rfbn_id: regions[user.rfbn_id] }
#     else:
#         list_regions=regions

#     SIZE_MAP = { 'large': 'большой', 'medium': 'средний', 'small': 'малый' }

#     log.info(f'MEET PROTOCOL. {len(rows)} : period: {period}, data: {data}')
#     for p in rows:
#         p['category'] = SIZE_MAP.get(p.get('category'), p.get('category') or '')

#         if isinstance(p.get('partners'), str):
#             p['partners'] = json.loads(p['partners'])
#         else:
#             p['partners'] = p.get('partners') or []

#         if isinstance(p.get('path_photo'), str):
#             p['path_photo'] = json.loads(p['path_photo'])
#         else:
#             p['path_photo'] = p.get('path_photo') or []

#     return RedirectResponse( url="/meet/protocol", status_code=303, )


