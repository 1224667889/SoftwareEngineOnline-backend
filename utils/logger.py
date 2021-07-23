import logging
logger = logging.getLogger('flask_manager')
logger.setLevel('DEBUG')

handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
logger.info("日志开启")

