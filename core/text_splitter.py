"""
text_splitter.py — 文本清洗、分段、重叠切片
基于LangChain的RecursiveCharacterTextSplitter实现
"""
from typing import List

from langchain_text_splitters import RecursiveCharacterTextSplitter
from utils.logger_util import get_logger
from config.settings import CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger("TextSplitter")


def split_text(
    text: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
    separators: List[str] = None,
) -> List[str]:
    """
    将长文本切分为带重叠的片段
    Args:
        text: 待切分的原始文本
        chunk_size: 每个片段的最大字符数
        chunk_overlap: 片段之间的重叠字符数
        separators: 分段优先使用的分隔符列表
    Returns:
        切分后的文本片段列表
    """
    if not text or not text.strip():
        logger.warning("输入文本为空，跳过切分")
        return []

    if separators is None:
        # 中文友好分隔符：优先按段落、句号、换行切分
        separators = ["\n\n", "\n", "。", "！", "？", "；", ".", "!", "?", ";", " ", ""]

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap,
        separators=separators,
        length_function=len,
    )

    chunks = splitter.split_text(text)
    logger.info(f"文本切分完成: 输入长度={len(text)}, 片段数={len(chunks)}, "
                f"chunk_size={chunk_size}, chunk_overlap={chunk_overlap}")
    return chunks


def split_text_with_metadata(
    text: str,
    source_filename: str,
    chunk_size: int = CHUNK_SIZE,
    chunk_overlap: int = CHUNK_OVERLAP,
) -> List[dict]:
    """
    切分文本并附带元数据
    Args:
        text: 待切分的原始文本
        source_filename: 来源文档文件名
        chunk_size: 每个片段的最大字符数
        chunk_overlap: 片段之间的重叠字符数
    Returns:
        包含文本和元数据的字典列表，格式: [{"text": str, "metadata": dict}, ...]
    """
    chunks = split_text(text, chunk_size, chunk_overlap)

    results = []
    for idx, chunk in enumerate(chunks):
        results.append({
            "text": chunk,
            "metadata": {
                "source": source_filename,
                "chunk_index": idx,
            }
        })

    logger.info(f"文本切分(含元数据)完成: 文档={source_filename}, 片段数={len(results)}")
    return results
