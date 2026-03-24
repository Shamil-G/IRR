import logging
from logging.handlers import RotatingFileHandler
from app.config.app_config import LOG_PATH
from app.config.gfss_parameter import debug, BASE


def init_logger():
    logger = logging.getLogger('IRR')
    # logging.getLogger('PDD').addHandler(logging.StreamHandler(sys.stdout))
    # Console
    logging.getLogger('IRR').addHandler(logging.StreamHandler())
    if debug:
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
        
    fh = logging.FileHandler(f"{BASE}/app/{LOG_PATH}/irr-pens.log", encoding="UTF-8")

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)

    logger.addHandler(fh)
    logger.info('Протокол для программы ИРР стартован...')
    return logger


log = init_logger()