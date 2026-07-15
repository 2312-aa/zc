"""Streamlit 前端入口：心理健康多智能体系统"""
import sys
from pathlib import Path

# 将项目根目录添加到 Python 路径
ROOT_DIR = Path(__file__).parent
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

import uuid
import streamlit as st
from datetime import datetime

# 初始化数据库
from db import init_db
from db.session import session_scope
from db.models import User

from graph import get_workflow
from config import CRISIS_HOTLINES


def init_page():
    """页面初始化配置"""
    st.set_page_config(
        page_title="心灵守护 - 心理健康智能助手",
        page_icon="🧠",
        layout="wide",
    )


def init_session_state():
    """初始化 Streamlit 会话状态"""
    if "user_id" not in st.session_state:
        st.session_state.user_id = str(uuid.uuid4())[:8]
    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = str(uuid.uuid4())
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "workflow" not in st.session_state:
        st.session_state.workflow = get_workflow()


def ensure_user_exists(user_id: str):
    """确保用户在数据库中存在"""
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id, nickname=f"用户{user_id}")
            db.add(user)


def main():
    init_page()
    init_session_state()
    init_db()

    # 确保用户存在
    ensure_user_exists(st.session_state.user_id)

    # ==================== 侧边栏 ====================
    with st.sidebar:
        st.title("🧠 心灵守护")
        st.caption("基于多智能体的心理健康助手")

        st.divider()

        # 用户信息
        st.subheader("个人信息")
        user_id = st.session_state.user_id
        st.text_input("用户ID", value=user_id, disabled=True)

        with session_scope() as db:
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                nickname = st.text_input("昵称", value=user.nickname or "", key="nickname_input")
                if nickname and nickname != (user.nickname or ""):
                    user.nickname = nickname

                risk_display = {
                    "low": "🟢 低风险",
                    "medium": "🟡 中风险",
                    "high": "🟠 高风险",
                    "crisis": "🔴 危机",
                }
                st.info(f"当前风险等级: {risk_display.get(user.risk_level, '🟢 低风险')}")

        st.divider()

        # 新会话
        if st.button("🔄 开始新会话", use_container_width=True):
            st.session_state.conversation_id = str(uuid.uuid4())
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # 危机热线
        st.subheader("☎️ 危机热线")
        for hotline in CRISIS_HOTLINES:
            st.markdown(f"- **{hotline['name']}**: {hotline['phone']}")

        st.divider()

        # 知识库管理
        st.subheader("📚 知识库")
        if st.button("加载知识库", use_container_width=True):
            with st.spinner("正在加载知识库..."):
                from rag.knowledge_loader import load_knowledge_to_vector_store
                load_knowledge_to_vector_store()
                st.success("知识库加载完成！")

        st.divider()
        st.caption("⚠️ 本系统仅为辅助工具，不能替代专业心理咨询。如遇危机情况，请拨打上方热线。")

    # ==================== 主聊天区 ====================
    st.title("💬 心理健康对话")

    # 显示历史消息
    for msg in st.session_state.messages:
        role = msg["role"]
        content = msg["content"]
        agent = msg.get("agent", "")

        if role == "user":
            with st.chat_message("user"):
                st.markdown(content)
        else:
            with st.chat_message("assistant"):
                if agent:
                    st.caption(f"🤖 {agent}")
                st.markdown(content)

    # 用户输入
    if prompt := st.chat_input("说出你的感受..."):
        # 显示用户消息
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "agent": "",
        })

        # 调用工作流
        with st.chat_message("assistant"):
            with st.spinner("思考中..."):
                try:
                    result = st.session_state.workflow.invoke({
                        "user_input": prompt,
                        "user_id": st.session_state.user_id,
                        "conversation_id": st.session_state.conversation_id,
                        "messages": [],
                        "retrieved_context": [],
                        "risk_assessment": None,
                        "next_agent": "",
                        "tool_results": {},
                        "turn_count": len(st.session_state.messages) // 2,
                        "is_crisis": False,
                    })

                    # 提取助手回复
                    ai_messages = result.get("messages", [])
                    if ai_messages:
                        response_content = ai_messages[-1].content
                    else:
                        response_content = "抱歉，我暂时无法回应，请稍后再试。"

                    # 确定智能体名称
                    next_agent = result.get("next_agent", "counseling")
                    agent_names = {
                        "counseling": "咨询助手",
                        "crisis": "危机干预师",
                        "resource": "资源推荐员",
                    }
                    agent_label = agent_names.get(next_agent, "助手")

                    # 风险评估信息
                    risk = result.get("risk_assessment")
                    if risk and risk.risk_level in ("high", "crisis"):
                        st.warning(f"⚠️ 检测到风险等级: {risk.risk_level} | 已转接{agent_label}")

                    st.caption(f"🤖 {agent_label}")
                    st.markdown(response_content)

                    # 保存消息
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": response_content,
                        "agent": agent_label,
                    })

                    # 保存到数据库
                    from tools.database_tools import save_conversation
                    save_conversation.invoke({
                        "conversation_id": st.session_state.conversation_id,
                        "user_id": st.session_state.user_id,
                        "role": "user",
                        "content": prompt,
                    })
                    save_conversation.invoke({
                        "conversation_id": st.session_state.conversation_id,
                        "user_id": st.session_state.user_id,
                        "role": "assistant",
                        "content": response_content,
                        "agent_name": next_agent,
                        "risk_score": risk.risk_score if risk else None,
                    })

                except Exception as e:
                    error_msg = f"抱歉，系统出现了一些问题：{str(e)}"
                    st.error(error_msg)
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": error_msg,
                        "agent": "系统",
                    })


if __name__ == "__main__":
    main()
