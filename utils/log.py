import logging
import logging.handlers as handlers
import os


#LOG_FILE_PATH = f'{os.environ["PYTHONPATH"]}/logs/server.log'

LOG_FILE_PATH = f'./logs/server.log'
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')

log_handler = handlers.TimedRotatingFileHandler(LOG_FILE_PATH, when='midnight')
log_handler.setFormatter(formatter)

console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(log_handler)
root_logger.addHandler(console_handler)
root_logger.setLevel(logging.INFO)

logger = logging.getLogger("logger")