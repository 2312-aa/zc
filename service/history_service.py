"""
history_service.py — 对话历史增删改查、本地文件持久化
支持按会话ID管理多组对话记录
"""
import json
import os
from datetime import datetime
from typing import List, Optional

from utils.logger_util import get_logger
from utils.exception_util import handle_exception
from utils.file_util import ensure_dir
from config.settings import CHAT_HISTORY_PATH

logger = get_logger("HistoryService")


class HistoryService:
    """对话历史管理服务"""

    def __init__(self, history_path: str = CHAT_HISTORY_PATH):
        self._history_path = history_path
        ensure_dir(history_path)

    def _get_session_file(self, session_id: str) -> str:
        """
        获取指定会话的历史记录文件路径
        Args:
            session_id: 会话ID
        Returns:
            文件绝对路径
        """
        safe_id = session_id.replace("/", "_").replace("\\", "_").replace("..", "")
        return os.path.join(self._history_path, f"{safe_id}.json")

    def _load_session(self, session_id: str) -> List[dict]:
        """
        从文件加载指定会话的历史记录
        Args:
            session_id: 会话ID
        Returns:
            对话记录列表
        """
        file_path = self._get_session_file(session_id)
        if not os.path.exists(file_path):
            return []
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except Exception as e:
            logger.error(f"加载会话历史失败: {session_id}, 原因: {str(e)}")
            return []

    def _save_session(self, session_id: str, records: List[dict]) -> None:
        """
        保存指定会话的历史记录到文件
        Args:
            session_id: 会话ID
            records: 对话记录列表
        """
        file_path = self._get_session_file(session_id)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(records, f, ensure_ascii=False, indent=2)
            logger.info(f"会话历史已保存: {session_id}, 记录数={len(records)}")
        except Exception as e:
            logger.error(f"保存会话历史失败: {session_id}, 原因: {str(e)}")

    def add_record(
        self,
        session_id: str,
        query: str,
        answer: str,
    ) -> None:
        """
        添加一轮对话记录
        Args:
            session_id: 会话ID
            query: 用户问题
            answer: 系统回答
        """
        records = self._load_session(session_id)
        record = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "query": query,
            "answer": answer,
        }
        records.append(record)
        self._save_session(session_id, records)

    def get_history(
        self,
        session_id: str,
        max_rounds: Optional[int] = None,
    ) -> List[dict]:
        """
        获取指定会话的对话历史
        Args:
            session_id: 会话ID
            max_rounds: 最大返回轮数，None表示全部
        Returns:
            对话记录列表
        """
        records = self._load_session(session_id)
        if max_rounds is not None and max_rounds > 0:
            records = records[-max_rounds:]
        return records

    def get_history_text(
        self,
        session_id: str,
        max_rounds: int = 5,
    ) -> str:
        """
        获取格式化的历史对话文本，用于拼接上下文
        Args:
            session_id: 会话ID
            max_rounds: 最大返回轮数
        Returns:
            格式化的历史对话文本
        """
        records = self.get_history(session_id, max_rounds)
        if not records:
            return ""

        parts = []
        for r in records:
            parts.append(f"用户: {r['query']}")
            parts.append(f"助手: {r['answer']}")
        return "\n".join(parts)

    def clear_session(self, session_id: str) -> None:
        """
        清空指定会话的历史记录
        Args:
            session_id: 会话ID
        """
        file_path = self._get_session_file(session_id)
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"会话历史已清空: {session_id}")
        else:
            logger.info(f"会话历史文件不存在: {session_id}")

    def get_all_sessions(self) -> List[str]:
        """
        获取所有会话ID列表
        Returns:
            会话ID列表
        """
        if not os.path.exists(self._history_path):
            return []
        sessions = []
        for f in os.listdir(self._history_path):
            if f.endswith(".json"):
                session_id = f[:-5]  # 去掉.json后缀
                sessions.append(session_id)
        return sorted(sessions)
