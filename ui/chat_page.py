"""
chat_page.py — 多轮对话问答页面
Streamlit前端页面，仅调用service层接口
"""
import streamlit as st

from core.vector_base.chroma_store import ChromaVectorStore
from service.chat_service import ChatService
from service.history_service import HistoryService
from utils.logger_util import get_logger
from config.settings import CHAT_HISTORY_PATH

logger = get_logger("ChatPage")


def _get_vector_store() -> ChromaVectorStore:
    """
    获取ChromaVectorStore实例（session_state缓存）
    Returns:
        ChromaVectorStore实例
    """
    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = ChromaVectorStore()
    return st.session_state["vector_store"]


def _get_chat_service() -> ChatService:
    """
    获取ChatService实例（session_state缓存）
    Returns:
        ChatService实例
    """
    if "chat_service" not in st.session_state:
        vector_store = _get_vector_store()
        history_service = _get_history_service()
        st.session_state["chat_service"] = ChatService(vector_store, history_service)
    return st.session_state["chat_service"]


def _get_history_service() -> HistoryService:
    """
    获取HistoryService实例（session_state缓存）
    Returns:
        HistoryService实例
    """
    if "history_service" not in st.session_state:
        st.session_state["history_service"] = HistoryService()
    return st.session_state["history_service"]


def render_chat_page():
    """渲染多轮对话问答页面"""

    # 页面标题
    st.title("💬 智能问答")
    st.markdown("---")

    # 初始化服务
    chat_service = _get_chat_service()
    history_service = _get_history_service()

    # 当前会话ID
    if "session_id" not in st.session_state:
        st.session_state["session_id"] = "default"
    session_id = st.session_state["session_id"]

    # ============================================================
    # 侧边栏：会话管理
    # ============================================================
    with st.sidebar:
        st.header("🔧 会话管理")

        # 新建会话
        new_session = st.text_input("新建会话ID", placeholder="输入会话名称")
        if st.button("📌 切换/新建会话", use_container_width=True):
            if new_session.strip():
                st.session_state["session_id"] = new_session.strip()
                st.rerun()

        st.markdown("---")

        # 当前会话信息
        st.info(f"当前会话: **{session_id}**")

        # 会话列表
        sessions = history_service.get_all_sessions()
        if sessions:
            st.write("历史会话：")
            for sid in sessions:
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button(f"📝 {sid}", key=f"switch_{sid}"):
                        st.session_state["session_id"] = sid
                        st.rerun()
                with col2:
                    if st.button("🗑️", key=f"del_session_{sid}"):
                        history_service.clear_session(sid)
                        if sid == session_id:
                            st.session_state["session_id"] = "default"
                        st.rerun()

        st.markdown("---")

        # 清空当前会话
        if st.button("🗑️ 清空当前会话", type="secondary", use_container_width=True):
            result = chat_service.clear_session(session_id)
            if result["success"]:
                st.success(result["message"])
            else:
                st.error(result["message"])
            st.rerun()

    # ============================================================
    # 主区域：对话展示
    # ============================================================
    # 加载历史对话记录并显示
    history_records = history_service.get_history(session_id)

    for record in history_records:
        with st.chat_message("user"):
            st.write(record["query"])
        with st.chat_message("assistant"):
            st.write(record["answer"])

    # ============================================================
    # 用户输入区域
    # ============================================================
    if prompt := st.chat_input("请输入您的问题..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.write(prompt)

        # 执行问答
        with st.chat_message("assistant"):
            with st.spinner("🤔 正在思考中..."):
                result = chat_service.chat(
                    query=prompt,
                    session_id=session_id,
                )

            if result["success"]:
                st.write(result["answer"])

                # 溯源信息展示（折叠面板）
                if result["sources"]:
                    with st.expander("📋 查看溯源信息", expanded=False):
                        for i, source in enumerate(result["sources"], 1):
                            st.markdown(f"**来源 {i}: {source['source']}**")
                            st.metric("相似度分数", f"{source['score']:.4f}")
                            st.text_area(
                                "原文片段",
                                value=source["text"],
                                height=100,
                                key=f"source_{i}_{hash(source['text'][:50])}",
                                disabled=True,
                            )
                            st.markdown("---")
            else:
                st.error(result["message"])
