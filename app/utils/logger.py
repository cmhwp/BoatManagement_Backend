import logging
import sys
from loguru import logger as loguru_logger
from pathlib import Path

# 创建日志目录
log_dir = Path("logs")
log_dir.mkdir(exist_ok=True)

# 移除默认处理器
loguru_logger.remove()

# 控制台输出
loguru_logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)

# 文件输出 - 普通日志
loguru_logger.add(
    "logs/app.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="DEBUG",
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)

# 文件输出 - 错误日志
loguru_logger.add(
    "logs/error.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    level="ERROR",
    rotation="10 MB",
    retention="30 days",
    compression="zip"
)

# 文件输出 - 访问日志
loguru_logger.add(
    "logs/access.log",
    format="{time:YYYY-MM-DD HH:mm:ss} | {message}",
    filter=lambda record: "ACCESS" in record["extra"],
    rotation="10 MB",
    retention="7 days",
    compression="zip"
)

logger = loguru_logger 