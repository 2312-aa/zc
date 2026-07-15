"""
logger_util.py — 全局分级日志工具
基于loguru实现，支持INFO/WARN/ERROR三级日志输出
"""
import sys
from loguru import logger
from config.settings import PROJECT_ROOT

# 移除默认handler
logger.remove()

# 日志文件存储目录
LOG_DIR = PROJECT_ROOT / "logs"
LOG_DIR.mkdir(exist_ok=True)

# 控制台输出：INFO及以上级别，精简格式
logger.add(
    sys.stderr,
    level="INFO",
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
           "<level>{level: <8}</level> | "
           "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
           "<level>{message}</level>",
    colorize=True,
)

# 文件输出：WARNING及以上级别，记录到文件
logger.add(
    str(LOG_DIR / "rag_system_{time:YYYY-MM-DD}.log"),
    level="WARNING",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="10 MB",
    retention="7 days",
    encoding="utf-8",
)

# 全部级别日志文件（用于调试）
logger.add(
    str(LOG_DIR / "rag_debug_{time:YYYY-MM-DD}.log"),
    level="DEBUG",
    format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
    rotation="50 MB",
    retention="3 days",
    encoding="utf-8",
)


def get_logger(name: str = "RAG"):
    """获取指定名称的logger实例"""
    return logger.bind(name=name)
