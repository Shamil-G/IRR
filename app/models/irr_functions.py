from app.db.connect import get_connection, select_one, plsql_execute_s, select
from app.core.logger import log
from datetime import datetime


def get_list_rayons(rfbn_id):
    stmt = f"""
        select rfbn_id, name
        from loader.branch b 
        where substr(b.rfbn_id,1,2)||'00'=:rfbn_id
        and   substr(b.rfbn_id,3)!='00'
    """
    full_stmt = f"""
        select rfbn_id, name
        from loader.branch b 
    """
    log.debug(f'GET LIST RAYONS for RFBN_ID: {rfbn_id}')

    if rfbn_id!='0000':
        args = {'rfbn_id': rfbn_id}
        records = select(stmt, args)
    else:
        args = {}
        records = select(full_stmt, args)
    log.debug(f'GET LIST RAYONS. RESULT: {records}')
    return records


def get_partners():
    stmt = f"""
        select value from params where param_name='partner'
    """
    args ={}
    records = select(stmt, args) 
    list_value = [item['value'] for item in records]
        
    log.debug(f'GET PARTNERS. RESULT: {list_value}')
    return list_value


def get_org_name(args)->str:
    stmt = f"select manage.get_org_name(:bin) as name from dual"

    nm = select_one(stmt, args)
    log.info(f'*** GET_ORG_NAME. args: {args}, nm: {nm}')
    return select_one(stmt, args)


def add_protocol(data: dict):
    cmd="""
    begin manage.add_protocol(:date_irr, :rfbn_id, :district, :cnt_total, 
                                :cnt_women, :bin, :meeting_format,
                                :category, :partners, :speaker, :employee,
                                :meeting_place, :path_photo); end;
    """
    if 'bin' not in data:
        data['bin']=''
    if 'category' not in data:
        data['category']=''
    if 'meeting_place' not in data:
        data['meeting_place']=''
    
    data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

    if 'organization_name' in data:
        data.pop('organization_name')

    plsql_execute_s('ADD_PROTOCOL', cmd, data)


def update_protocol(data: dict):
    cmd="""
    begin manage.update_protocol(:prot_num, :date_irr, :rfbn_id, :district, :cnt_total, 
                                :cnt_women, :bin, :meeting_format,
                                :category, :partners, :speaker, :employee,
                                :meeting_place, :path_photo); end;
    """
    log.debug(f'UPDATE_PROTOCOL: {len(data)} : {data}')
    data['date_irr']=datetime.strptime(data['date_irr'], "%Y-%m-%d").date()

    if 'bin' not in data:
        data['bin']=''
    if 'category' not in data:
        data['category']=''
    if 'meeting_place' not in data:
        data['meeting_place']=''
    
    if 'organization_name' in data:
        data.pop('organization_name')
    plsql_execute_s('ADD_PROTOCOL', cmd, data)


def get_rows(params):
    cmd="""
        select l.date_irr,
               l.prot_num, 
               l.status,
               l.rfbn_id,
               district, 
               b.name,
               cnt_total, cnt_women, 
               speaker, 
               meeting_format,        
               partners, 
               bin, 
               case when bin is null then 'Встреча с населением'
                    else ( select p_name from loader.pmpd_pay_doc pd where pd.p_rnn=bin and rownum=1)
                    end org_name, 
               meeting_place, 
               category, 
               path_photo, 
               employee 
        from list_protocol l, loader.branch b
        where l.district=b.rfbn_id
        and   date_irr>=trunc(sysdate,'YY')
        and   l.rfbn_id = 
                case when :top_view=1
                     then l.rfbn_id
                     else substr(:rfbn_id,1,2)
                end
        and to_char(date_irr, 'YYYY-MM')=:period
        order by status asc, date_irr desc               
    """
    rows = select(cmd, params)
    for p in rows:
        for key, value in p.items(): 
            if value is None: p[key] = ''
    log.debug(f'LIST_PROTOCOLS. PARAMS {params}, RESULT LEN: {len(rows)}\n*** ROWS: {rows}')

    return rows


def set_action(f_name, proc_name, args):
    plsql_execute_s(f_name, proc_name, args)


def load_protocol(prot_num):
    stmt = "select * from list_protocol where prot_num=:protocol_num"
    params = {'protocol_num': prot_num}
    result = select_one(stmt, params)
    for key, value in result.items(): 
        if value is None: result[key] = ''
    log.debug(f'--->\n\tLOAD PROTOCOL:\n\tRESULT: {result}\n<---')
    return result

