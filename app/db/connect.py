from    contextlib import contextmanager
import  oracledb
import  app.config.db_config as cfg
from    app.config.gfss_parameter import LD_LIBRARY_PATH, platform
from    app.core.logger import log


def init_session(connection, requestedTag_ignored):
    cursor = connection.cursor()
    cursor.execute("ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
    cursor.execute("ALTER SESSION SET NLS_NUMERIC_CHARACTERS = ', '")
    log.debug("--------------> Executed: ALTER SESSION SET NLS_DATE_FORMAT = 'DD.MM.YYYY HH24:MI'")
    cursor.close()

if platform == 'unix':
    oracledb.init_oracle_client(lib_dir=LD_LIBRARY_PATH)

_pool = oracledb.create_pool(user=cfg.username, 
                             password=cfg.password, 
                             host=cfg.host,
                             port=cfg.port,
                             service_name=cfg.service,
                             timeout=cfg.timeout, 
                             wait_timeout=cfg.wait_timeout,
                             max_lifetime_session=cfg.max_lifetime_session, 
                             expire_time=cfg.expire_time,
                             tcp_connect_timeout=cfg.tcp_connect_timeout, 
                             min=cfg.pool_min, 
                             max=cfg.pool_max, 
                             increment=cfg.pool_inc,
                             session_callback=init_session)
log.info(f"Пул соединенй БД Oracle создан. DB: {cfg.host}:{cfg.port}/{cfg.service}")


def get_connection():
    global _pool
    return _pool.acquire()


def close_connection(connection):
    global _pool
    _pool.release(connection)


@contextmanager
def get_cursor():
   conn = get_connection()
   try:
       cursor = conn.cursor()
       yield cursor
   finally:
       cursor.close()
       close_connection(conn)


def get_db():
    conn = get_connection()
    try:
        yield conn
    finally:
        close_connection(conn)


def is_english_column(name: str) -> bool: 
    return all(c.isascii() and (c.isalnum() or c == '_') for c in name)


def select(stmt: str, params: dict | None=None) -> list[dict]:
    results = []
    try:
        with get_cursor() as cursor:
            cursor.execute(stmt, params or {})

            columns = [ col[0].lower() if is_english_column(col[0]) else col[0] for col in cursor.description ]

            for row in cursor.fetchall():
                results.append(dict(zip(columns, row)))
            return results
    except oracledb.DatabaseError as e:
        error, = e.args
        err_message = f'STMT: {stmt}\nPARAMS: {params}\n\t{error.code} : {error.message}'
        log.error(f"------select------> ERROR\n{err_message}\n")
        return []


def select_one(stmt: str, args: dict | None=None) -> dict:
    result = {}
    try:
        with get_cursor() as cursor:
            cursor.execute(stmt, args)
            columns = [ col[0].lower() if is_english_column(col[0]) else col[0] for col in cursor.description ]
            row = cursor.fetchone()
            if row:
                result=dict(zip(columns, row))
            return result
    except oracledb.DatabaseError as e:
        error, = e.args
        err_message = f'STMT: {stmt}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"------select------> ERROR\n\t{err_message}")
        log.error(err_message)
        return {}


def plsql_execute(cursor, proc_name, cmd, args):
    err_message = ''
    status='success'
    try:
        cursor.execute(cmd, args)
        log.debug(f"------execute------> INFO. {proc_name}\ncmd: {cmd}\nargs: {args}")
        return status, f'{err_message}'
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_message = f'{proc_name}:{cmd}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"------execute------> ERROR\n\t{err_message}")
        return status, f'{err_message}'


def plsql_execute_s(f_name, proc_name, args):
    with get_cursor() as cursor:
        return plsql_execute(cursor, f_name, proc_name, args)


def plsql_proc(cursor, f_name, proc_name, args):
    err_message = ''
    status='success'
    try:
        cursor.callproc(proc_name, args)
        log.debug(f"------plsql_proc------> INFO. \n\tf_name: {f_name}\n\tproc_name: {proc_name}\n\targs: {args}")
        return status, err_message
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_message = f'{f_name}:{proc_name}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"-----plsql-proc-----> ERROR. {err_message}")
        return status, err_message


def plsql_proc_s(f_name, proc_name, args):
    with get_cursor() as cursor:
        return plsql_proc(cursor, f_name, proc_name, args)


def plsql_func(cursor, f_name, func_name, args):
    ret = ''
    err_mess = ''
    status='success'
    try:
        ret = cursor.callfunc(func_name, str, args)
        return status, ret, err_mess
    except oracledb.DatabaseError as e:
        error, = e.args
        status='fail'
        err_mess = f'{f_name}:{func_name}\n\tARGS: {args}\n\t{error.code} : {error.message}'
        log.error(f"-----plsql-func-----> ERROR. {err_mess}")
        return status, ret, err_mess


def plsql_func_s(f_name, proc_name, args):
    with get_cursor() as cursor:
        return plsql_func(cursor, f_name, proc_name, args)


if __name__ == "__main__":
    print("Тестируем CONNECT блок!")
    with get_db() as con:
        print("Версия: " + con.version)
        val = "Hello from main"

