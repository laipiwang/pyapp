import time
import logging
from functools import wraps


def timing_decorator(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        logger = logging.getLogger('stock_analysis')
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        execution_time = end_time - start_time
        logger.info(f"{func.__name__} 執行時間: {execution_time:.2f} 秒")
        return result
    return wrapper


def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger = logging.getLogger('stock_analysis')
            logger.error(f"執行 {func.__name__} 時發生錯誤: {str(e)}")
            # 添加更詳細的錯誤信息
            logger.exception("詳細錯誤信息:")
            raise
    return wrapper
