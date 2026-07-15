"""数据库工具：用户档案、会话存储查询"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_core.tools import tool

from db.session import session_scope
from db.models import User, Conversation, Message


@tool
def get_user_profile(user_id: str) -> str:
    """查询用户档案信息，包括昵称、年龄、风险等级等。

    Args:
        user_id: 用户唯一标识
    """
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            return f"未找到用户 {user_id} 的档案"
        return (
            f"用户ID: {user.user_id}\n"
            f"昵称: {user.nickname or '未设置'}\n"
            f"年龄: {user.age or '未设置'}\n"
            f"性别: {user.gender or '未设置'}\n"
            f"风险等级: {user.risk_level}\n"
            f"注册时间: {user.created_at}"
        )


@tool
def save_conversation(
    conversation_id: str,
    user_id: str,
    role: str,
    content: str,
    agent_name: str = None,
    risk_score: float = None,
) -> str:
    """保存一条对话消息到数据库。

    Args:
        conversation_id: 会话ID
        user_id: 用户ID
        role: 消息角色 (user/assistant/system)
        content: 消息内容
        agent_name: 生成该消息的智能体名称
        risk_score: 风险评分 0-1
    """
    with session_scope() as db:
        # 确保会话存在
        conv = db.query(Conversation).filter(
            Conversation.conversation_id == conversation_id
        ).first()
        if not conv:
            conv = Conversation(
                conversation_id=conversation_id,
                user_id=user_id,
            )
            db.add(conv)
            db.flush()

        msg = Message(
            conversation_id=conversation_id,
            role=role,
            content=content,
            agent_name=agent_name,
            risk_score=risk_score,
        )
        db.add(msg)

        # 更新会话风险等级
        if risk_score and risk_score > 0.6:
            conv.risk_level = "high" if risk_score < 0.8 else "crisis"
            # 同时更新用户风险等级
            user = db.query(User).filter(User.user_id == user_id).first()
            if user:
                user.risk_level = conv.risk_level

    return "消息已保存"


@tool
def get_conversation_history(conversation_id: str, limit: int = 20) -> str:
    """获取指定会话的历史消息。

    Args:
        conversation_id: 会话ID
        limit: 返回消息数量上限
    """
    with session_scope() as db:
        messages = (
            db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.created_at.desc())
            .limit(limit)
            .all()
        )
        if not messages:
            return "暂无历史消息"

        # 按时间正序排列
        messages = list(reversed(messages))
        lines = []
        for msg in messages:
            prefix = "用户" if msg.role == "user" else f"AI({msg.agent_name or '助手'})"
            lines.append(f"[{prefix}] {msg.content}")

        return "\n".join(lines)


@tool
def create_or_update_user(
    user_id: str,
    nickname: str = None,
    age: int = None,
    gender: str = None,
) -> str:
    """创建或更新用户档案。

    Args:
        user_id: 用户唯一标识
        nickname: 昵称
        age: 年龄
        gender: 性别
    """
    with session_scope() as db:
        user = db.query(User).filter(User.user_id == user_id).first()
        if not user:
            user = User(user_id=user_id)
            db.add(user)
            db.flush()

        if nickname:
            user.nickname = nickname
        if age:
            user.age = age
        if gender:
            user.gender = gender

    return f"用户 {user_id} 档案已更新"
