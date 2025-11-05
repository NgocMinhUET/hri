"""
Logger - Hệ thống logging cho bot
"""
import logging
import sys
from pathlib import Path

def setup_logger(name="UETBot", level=logging.INFO, log_file=None):
    """
    Tạo logger với format đẹp
    
    Args:
        name: Tên logger
        level: Mức độ log (DEBUG, INFO, WARNING, ERROR)
        log_file: Đường dẫn file log (optional)
    
    Returns:
        Logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Tránh duplicate handlers
    if logger.handlers:
        return logger
    
    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (nếu có)
    if log_file:
        Path("logs").mkdir(exist_ok=True)
        file_handler = logging.FileHandler(f"logs/{log_file}", encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger

