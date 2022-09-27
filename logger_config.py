from loguru import logger

logger.add('errors_log.log', format="{time} {level} {message}", level='DEBUG', rotation='1 MB', compression='zip')
