"""
ollama_embed_factory.py — 向量嵌入模型全局单例工厂
确保Embedding模型全局唯一实例，避免Streamlit反复刷新重复创建连接
"""
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_ollama import OllamaEmbeddings
from utils.logger_util import get_logger
from utils.exception_util import EmbeddingError
from config.llm_emb_config import OLLAMA_BASE_URL, OLLAMA_EMBED_MODEL
from config.settings import RETRIEVE_TOP_K

logger = get_logger("EmbedFactory")

# 全局单例缓存
_embed_instance: OllamaEmbeddings = None


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(
        f"Embedding模型调用重试中... 第{retry_state.attempt_number}次"
    ),
)
def _create_embed_instance() -> OllamaEmbeddings:
    """
    创建OllamaEmbeddings实例（带重试机制）
    Returns:
        OllamaEmbeddings实例
    """
    try:
        instance = OllamaEmbeddings(
            model=OLLAMA_EMBED_MODEL,
            base_url=OLLAMA_BASE_URL,
        )
        logger.info(f"Embedding模型实例创建成功: {OLLAMA_EMBED_MODEL}")
        return instance
    except Exception as e:
        raise EmbeddingError(
            f"Embedding模型创建失败: {OLLAMA_EMBED_MODEL}",
            detail=str(e)
        )


def get_embed_instance() -> OllamaEmbeddings:
    """
    获取Embedding模型全局单例
    Returns:
        OllamaEmbeddings实例
    """
    global _embed_instance
    if _embed_instance is None:
        logger.info("首次创建Embedding模型实例...")
        _embed_instance = _create_embed_instance()
    return _embed_instance


def reset_embed_instance() -> None:
    """重置Embedding模型单例（用于异常恢复）"""
    global _embed_instance
    _embed_instance = None
    logger.info("Embedding模型单例已重置")
