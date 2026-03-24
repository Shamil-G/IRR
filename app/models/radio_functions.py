from datetime import datetime

from app.db.connect import select_one, plsql_execute_s, select
from app.core.logger  import log
from app.models.radio_functions import *


def add(data: dict):
    cmd="""
    begin radio.add(:event_date, :rfbn_id, :channel_name, :speaker, :description, :employee); end;
    """
    data['event_date']=datetime.strptime(data['event_date'], "%Y-%m-%d").date()
    plsql_execute_s('ADD_RADIO', cmd, data)


def upd(data: dict):
    cmd="""
    begin radio.upd(:prot_num, :event_date, :rfbn_id, :channel_name, :speaker, :description, :employee); end;
    """
    log.info(f'UPDATE_RADIO: {len(data)} : {data}')
    data['event_date']=datetime.strptime(data['event_date'], "%Y-%m-%d").date()

    plsql_execute_s('UPD RADIO', cmd, data)


def get_rows(params):
    cmd="""
        select prot_num, 
               l.event_date,
               l.status,
               l.rfbn_id,
               b.name,
               l.prot_num,
               l.channel_name, 
               l.speaker,
               l.description, 
               l.employee 
        from radio_events l, loader.branch b
        where l.rfbn_id||'00'=b.rfbn_id
        and   l.rfbn_id = 
                case when :top_view=1
                     then l.rfbn_id
                     else substr(:rfbn_id,1,2)
                end
        and to_char(event_date, 'YYYY-MM')=:period
        order by status asc, event_date desc
    """
    rows = select(cmd, params)
    for p in rows:
        for key, value in p.items(): 
            if value is None: p[key] = ''
    log.info(f'RADIO. PARAMS {params}')

    return rows


def set_action(f_name, proc_name, args):
    plsql_execute_s(f_name, proc_name, args)


def load_protocol(prot_num):
    stmt = "select * from radio_events where prot_num=:protocol_num"
    params = {'protocol_num': prot_num}
    result = select_one(stmt, params)
    for key, value in result.items(): 
        if value is None: result[key] = ''
    log.info(f'--->\n\tLOAD RADIO EVENT:\n\tRESULT: {result}\n<---')
    return result

