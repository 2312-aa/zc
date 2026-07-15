"""
rag_chain_builder.py — 完整RAG链路构建器
召回→相似度过滤→问答组装，串联向量检索与LLM生成
"""
from typing import List

from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from langchain_ollama import OllamaLLM
from core.vector_base.chroma_store import ChromaVectorStore
from utils.logger_util import get_logger
from utils.exception_util import LLMGenerateError
from config.llm_emb_config import (
    OLLAMA_BASE_URL,
    OLLAMA_LLM_MODEL,
    LLM_TEMPERATURE,
    LLM_NUM_CTX,
)
from config.settings import (
    RETRIEVE_TOP_K,
    SIMILARITY_THRESHOLD,
    RETRIEVE_TOP_N,
)

logger = get_logger("RAGChainBuilder")

# 全局LLM单例
_llm_instance: OllamaLLM = None


def _get_llm_instance() -> OllamaLLM:
    """获取LLM全局单例"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = OllamaLLM(
            model=OLLAMA_LLM_MODEL,
            base_url=OLLAMA_BASE_URL,
            temperature=LLM_TEMPERATURE,
            num_ctx=LLM_NUM_CTX,
        )
        logger.info(f"LLM模型实例创建成功: {OLLAMA_LLM_MODEL}")
    return _llm_instance


# RAG系统Prompt模板
RAG_PROMPT_TEMPLATE = """你是一位资深Web安全工程师，专注于Web漏洞分析与防御。请严格根据以下参考内容回答用户的问题。

回答要求：
1. 优先依据参考内容作答，回答应详细、专业、结构清晰
2. 涉及漏洞类型时，按"原理→分类→攻击手法→危害→防御措施"的逻辑组织回答
3. 适当补充代码示例、攻击载荷示例和防御代码示例，帮助理解
4. 如需对比多种漏洞，用表格或分点方式清晰展示差异
5. 如果参考内容中没有相关信息，请明确回答"根据知识库内容，无法回答该问题"，不要自行编造内容
6. 回答使用中文，技术术语保留英文原文

参考内容：
{context}

用户问题：{question}

请根据以上参考内容，给出详细、专业的回答："""


def retrieve(
    query: str,
    vector_store: ChromaVectorStore,
    top_k: int = RETRIEVE_TOP_K,
    similarity_threshold: float = SIMILARITY_THRESHOLD,
    top_n: int = RETRIEVE_TOP_N,
) -> List[dict]:
    """
    向量召回 + 相似度过滤 + 取Top-N
    Args:
        query: 用户查询
        vector_store: 向量库实例
        top_k: 初次召回数量
        similarity_threshold: 向量相似度阈值
        top_n: 最终返回的最大片段数
    Returns:
        检索结果列表，格式: [{"text": str, "metadata": dict, "score": float}, ...]
    """
    logger.info(f"开始检索流程: query={query[:50]}..., top_k={top_k}")

    # 1. 向量召回Top-K片段
    raw_results = vector_store.similarity_search(query, top_k=top_k)

    # 2. 按相似度阈值过滤
    filtered_results = [r for r in raw_results if r["score"] >= similarity_threshold]
    logger.info(f"向量召回: 原始={len(raw_results)}, 相似度阈值过滤后={len(filtered_results)}")

    # 3. 取Top-N（已按相似度降序排列）
    final_results = filtered_results[:top_n]

    logger.info(f"检索完成: 最终结果数={len(final_results)}")
    return final_results


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    retry=retry_if_exception_type(Exception),
    before_sleep=lambda retry_state: logger.warning(
        f"LLM生成重试中... 第{retry_state.attempt_number}次"
    ),
)
def generate_answer(
    query: str,
    context: str,
    chat_history: str = "",
) -> str:
    """
    基于检索上下文生成回答
    Args:
        query: 用户问题
        context: 检索到的上下文内容
        chat_history: 历史对话上下文
    Returns:
        LLM生成的回答文本
    """
    try:
        llm = _get_llm_instance()

        # 拼接完整prompt
        if chat_history:
            full_prompt = f"以下是之前的对话历史：\n{chat_history}\n\n"
        else:
            full_prompt = ""

        full_prompt += RAG_PROMPT_TEMPLATE.format(
            context=context,
            question=query,
        )

        logger.info(f"开始LLM生成: prompt长度={len(full_prompt)}")
        answer = llm.invoke(full_prompt)
        logger.info(f"LLM生成完成: 回答长度={len(answer)}")
        return answer

    except Exception as e:
        raise LLMGenerateError(
            "LLM生成回答失败",
            detail=str(e)
        )


def build_rag_answer(
    query: str,
    vector_store: ChromaVectorStore,
    chat_history: str = "",
) -> dict:
    """
    完整RAG链路：用户Query → 向量召回 → 相似度过滤 → 拼接上下文+历史 → LLM生成答案
    Args:
        query: 用户问题
        vector_store: 向量库实例
        chat_history: 历史对话上下文
    Returns:
        {
            "answer": str,             # LLM生成的回答
            "sources": List[dict],     # 溯源信息列表
        }
    """
    logger.info(f"完整RAG链路开始: query={query[:50]}...")

    # 1. 检索
    retrieved = retrieve(query, vector_store)

    if not retrieved:
        return {
            "answer": "抱歉，在知识库中未找到与您问题相关的内容，请尝试换个表述或上传相关文档。",
            "sources": [],
        }

    # 2. 拼接检索上下文
    context_parts = []
    for i, r in enumerate(retrieved, 1):
        context_parts.append(f"[参考内容{i}]\n{r['text']}")
    context = "\n\n".join(context_parts)

    # 3. LLM生成回答
    answer = generate_answer(query, context, chat_history)

    # 4. 整理溯源信息
    sources = []
    for r in retrieved:
        sources.append({
            "source": r["metadata"].get("source", "未知文档"),
            "score": round(r["score"], 4),
            "text": r["text"][:200] + ("..." if len(r["text"]) > 200 else ""),
        })

    logger.info(f"RAG链路完成: 回答长度={len(answer)}, 溯源数={len(sources)}")
    return {
        "answer": answer,
        "sources": sources,
    }
