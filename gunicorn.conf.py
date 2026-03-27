import multiprocessing
from app.config.gfss_parameter import app_home, app_name
from app.config.app_config import port

bind = f"localhost:{port}"
#bind = f"192.168.1.34:{port}"
workers = multiprocessing.cpu_count()

worker_class = "uvicorn.workers.UvicornWorker"

reload=False 

chdir = f"{app_home}/{app_name}"
wsgi_app = "app.main:app"
loglevel = 'info'

access_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"  "%(a)s"'
accesslog = "logs/irr-gunicorn-access.log"
error_log_format = '%({x-forwarded-for}i)s %(l)s %(u)s %(t)s "%(r)s" %(s)s %(b)s "%(f)s"  "%(a)s"'
errorlog = "logs/irr-gunicorn-error.log"
proc_name = 'IRR-GFSS'
# Перезапуск после N кол-во запросов
max_requests = 10000
# Перезапуск, если ответа не было более 60 сек
timeout = 30
# umask or -m 007
umask = 0x007
