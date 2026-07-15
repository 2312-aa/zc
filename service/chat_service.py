"""
chat_service.py — 多轮问答业务服务层
多轮问答、上下文拼接、溯源信息整理
UI层仅调用该层接口
"""
from typing import List, Optional

from core.vector_base.chroma_store import ChromaVectorStore
from core.rag_chain_builder import build_rag_answer
from service.history_service import HistoryService
from utils.logger_util import get_logger
from utils.exception_util import handle_exception
from config.settings import CHAT_HISTORY_PATH

logger = get_logger("ChatService")


class ChatService:
    """多轮问答业务服务"""

    def __init__(
        self,
        vector_store: ChromaVectorStore,
        history_service: Optional[HistoryService] = None,
    ):
        self._vector_store = vector_store
        self._history_service = history_service or HistoryService()

    def chat(
        self,
        query: str,
        session_id: str = "default",
        max_history_rounds: int = 5,
    ) -> dict:
        """
        执行一次完整的RAG问答
        Args:
            query: 用户问题
            session_id: 会话ID
            max_history_rounds: 携带的最大历史对话轮数
        Returns:
            {
                "answer": str,              # 回答内容
                "sources": List[dict],      # 溯源信息
                "success": bool,            # 是否成功
                "message": str,             # 提示信息
            }
        """
        try:
            # 1. 获取历史对话上下文
            chat_history = self._history_service.get_history_text(
                session_id=session_id,
                max_rounds=max_history_rounds,
            )

            # 2. 执行RAG链路
            result = build_rag_answer(
                query=query,
                vector_store=self._vector_store,
                chat_history=chat_history,
            )

            # 3. 保存本次问答到历史记录
            self._history_service.add_record(
                session_id=session_id,
                query=query,
                answer=result["answer"],
            )

            logger.info(f"问答完成: session={session_id}, query长度={len(query)}, "
                        f"answer长度={len(result['answer'])}")

            return {
                "answer": result["answer"],
                "sources": result["sources"],
                "success": True,
                "message": "问答成功",
            }

        except Exception as e:
            error_msg = handle_exception(e)
            logger.error(f"问答失败: session={session_id}, 原因: {error_msg}")
            return {
                "answer": "",
                "sources": [],
                "success": False,
                "message": f"问答失败: {error_msg}",
            }

    def clear_session(self, session_id: str = "default") -> dict:
        """
        清空指定会话的历史记录
        Args:
            session_id: 会话ID
        Returns:
            {"success": bool, "message": str}
        """
        try:
            self._history_service.clear_session(session_id)
            return {
                "success": True,
                "message": "会话历史已清空",
            }
        except Exception as e:
            error_msg = handle_exception(e)
            return {
                "success": False,
                "message": f"清空失败: {error_msg}",
            }
