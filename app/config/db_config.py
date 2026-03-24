from app.config.gfss_parameter import platform, debug

if platform == 'unix':
    pool_min = 1
    pool_max = 40
    pool_inc = 4
else:
    pool_min = 1
    pool_max = 40
    pool_inc = 1

username = 'irr'
password = 'irr'
host = '192.168.20.60'
port = 1521
service = 'gfssdb.gfss.kz'

expire_time = 2 # количество минут между отправкой keepalive
tcp_connect_timeout = 5 # Максимальное время ожидания установления соединения
timeout = 300       # В секундах. Время простоя, после которого курсор освобождается
wait_timeout = 2000  # Время (в миллисекундах) ожидания доступного сеанса в пуле, перед тем как выдать ошибку
max_lifetime_session = 7200  # Время в секундах, в течении которого может существоват сеанс
retry_count = 1
retry_delay = 2




