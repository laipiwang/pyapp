import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime
from .config_loader import ConfigLoader


def setup_logging(name: str = 'stock_analysis') -> logging.Logger:
    """
    配置並返回日誌記錄器

    Args:
        name: 日誌記錄器名稱

    Returns:
        logging.Logger: 配置好的日誌記錄器
    """
    try:
        # 獲取配置
        config = ConfigLoader().get_config()
        log_config = config['logging']
        log_dir = Path(config['base']['logs_dir'])

        # 創建日誌目錄
        log_dir.mkdir(exist_ok=True)

        # 設置日誌文件名
        log_file = log_dir / f"stock_analysis_{datetime.now():%Y%m%d}.log"

        # 獲取或創建日誌記錄器
        logger = logging.getLogger(name)
        logger.setLevel(logging.INFO)

        # 清除現有的處理器
        if logger.hasHandlers():
            logger.handlers.clear()

        # 創建文件處理器
        file_handler = RotatingFileHandler(
            filename=str(log_file),
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))

        # 創建控制台處理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(logging.Formatter(
            '%(message)s'
        ))

        # 添加處理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

        logger.info(f"日誌系統初始化完成，日誌文件: {log_file}")
        return logger

    except Exception as e:
        # 如果配置失敗，使用基本配置
        basic_logger = _setup_basic_logger(name)
        basic_logger.error(f"日誌系統配置失敗，使用基本配置: {str(e)}")
        return basic_logger


def _setup_basic_logger(name: str) -> logging.Logger:
    """
    設置基本的日誌記錄器（當主要配置失敗時使用）

    Args:
        name: 日誌記錄器名稱

    Returns:
        logging.Logger: 基本配置的日誌記錄器
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    # 清除現有的處理器
    if logger.hasHandlers():
        logger.handlers.clear()

    # 創建基本的控制台處理器
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s'
    ))
    logger.addHandler(console_handler)

    # 嘗試創建基本的文件處理器
    try:
        log_dir = Path('logs')
        log_dir.mkdir(exist_ok=True)

        file_handler = RotatingFileHandler(
            filename=log_dir / 'stock_analysis.log',
            maxBytes=1024*1024,  # 1MB
            backupCount=3,
            encoding='utf-8'
        )
        file_handler.setFormatter(logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        ))
        logger.addHandler(file_handler)

    except Exception as e:
        logger.error(f"無法創建日誌文件: {str(e)}")

    return logger
