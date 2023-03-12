from pathlib import Path
import os
import logging

BASE_DIR = Path(__file__).resolve().parent.parent
LOGGING_PATH = os.path.join(BASE_DIR, 'log', "template.log")

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# create a file handler and set its level to DEBUG
file_handler = logging.FileHandler(LOGGING_PATH)
file_handler.setLevel(logging.DEBUG)

# create a console handler and set its level to ERROR
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)

# create a formatter and set it to the handlers
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
file_handler.setFormatter(formatter)
console_handler.setFormatter(formatter)

# add the handlers to the logger
logger.addHandler(file_handler)
logger.addHandler(console_handler)


def insert_log(message, file_name, line, level):
    text = f'[{message}] (File: {file_name}, Line:{line})'
    if level in ("debug", "Debug", "DEBUG"):
        logger.debug(text)
    if level in ("info", "Info", "INFO"):
        logger.info(text)
    if level in (text):
        logger.warning(text)
    if level in ("error", "Error", "ERROR"):
        logger.error(text)