"""检索器封装：基于 ChromaDB 的相似度检索"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.vectorstores import Chroma

from config import RAG_TOP_K
from rag.vector_store import get_vector_store


def get_retriever(search_type: str = "similarity", top_k: int = None):
    """获取检索器

    Args:
        search_type: 检索类型，支持 similarity / mmr / similarity_score_threshold
        top_k: 返回文档数量
    """
    vector_store = get_vector_store()
    k = top_k or RAG_TOP_K
    search_kwargs = {"k": k}
    if search_type == "mmr":
        search_kwargs["fetch_k"] = k * 4
        search_kwargs["lambda_mult"] = 0.7
    elif search_type == "similarity_score_threshold":
        search_kwargs["score_threshold"] = 0.5

    return vector_store.as_retriever(
        search_type=search_type,
        search_kwargs=search_kwargs,
    )


def retrieve_documents(query: str, top_k: int = None) -> list[dict]:
    """检索与查询相关的文档

    Args:
        query: 用户查询文本
        top_k: 返回数量

    Returns:
        包含 content 和 metadata 的字典列表
    """
    vector_store = get_vector_store()
    k = top_k or RAG_TOP_K
    docs = vector_store.similarity_search_with_score(query, k=k)
    results = []
    for doc, score in docs:
        results.append({
            "content": doc.page_content,
            "metadata": doc.metadata,
            "score": float(score),
        })
    return results
