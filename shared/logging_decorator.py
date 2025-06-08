import logging
from functools import wraps

# --- Configuration ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='bot.log',
    filemode='w',
    encoding='utf-8'
)
logger = logging.getLogger(__name__)

call_count = 0
symbol = "*"

def log(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        global call_count
        # Входные данные
        logger.info(f"{symbol* call_count}Call: {func.__name__} with args={str(args)} kwargs={str(kwargs)}")
        call_count += 1
        try:
            result = func(*args, **kwargs)
            # Выходные данные
            logger.info(f"{symbol* (call_count-1)}Done: {func.__name__} result={result}")
            call_count-=1
            return result
        except Exception as e:
            logger.exception(f"Exception {e.__name__} in {func.__name__}")
            raise
    return wrapper

def log_exception(e, func_name):
    logger.exception(f"{func_name} produced exception - {e}")