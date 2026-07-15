"""
exception_util.py — 自定义业务异常统一捕获
前端展示友好中文提示，不直接抛出原始代码堆栈
"""
from utils.logger_util import get_logger

logger = get_logger("Exception")


class RAGSystemException(Exception):
    """RAG系统基础业务异常"""

    def __init__(self, message: str, detail: str = ""):
        self.message = message          # 用户友好的中文提示
        self.detail = detail            # 详细错误信息（仅记录日志）
        super().__init__(self.message)
        if detail:
            logger.error(f"[{self.__class__.__name__}] {message} | 详情: {detail}")
        else:
            logger.error(f"[{self.__class__.__name__}] {message}")


class OllamaServiceError(RAGSystemException):
    """Ollama服务连接或调用异常"""
    pass


class FileParseError(RAGSystemException):
    """文档解析异常"""
    pass


class VectorStoreError(RAGSystemException):
    """向量库操作异常"""
    pass


class EmbeddingError(RAGSystemException):
    """向量化嵌入异常"""
    pass


class RerankError(RAGSystemException):
    """重排模型调用异常"""
    pass


class LLMGenerateError(RAGSystemException):
    """大模型生成异常"""
    pass


class FileValidationError(RAGSystemException):
    """文件校验异常"""
    pass


class ModelNotReadyError(RAGSystemException):
    """模型未就绪异常"""
    pass


def handle_exception(e: Exception) -> str:
    """
    统一异常处理：将异常转换为用户友好的中文提示
    Args:
        e: 捕获的异常
    Returns:
        用户友好的中文错误提示
    """
    if isinstance(e, RAGSystemException):
        return e.message

    # 未知异常统一处理
    logger.exception(f"未预期的异常: {str(e)}")
    return "系统内部错误，请稍后重试或联系管理员"
