"""LangGraph 图状态 Schema"""
from typing import Annotated, Literal
from typing_extensions import TypedDict
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class RiskAssessment(BaseModel):
    """风险评估结果"""
    risk_level: Literal["low", "medium", "high", "crisis"] = Field(
        default="low", description="风险等级"
    )
    risk_score: float = Field(default=0.0, ge=0.0, le=1.0, description="风险评分 0-1")
    intent: str = Field(default="general", description="用户意图分类")
    reasoning: str = Field(default="", description="判断理由")


class ConversationState(TypedDict):
    """多智能体对话状态

    所有节点共享此状态，通过消息列表追踪对话历史。
    """
    # 对话核心
    messages: Annotated[list, add_messages]          # 消息历史（LangGraph 自动追加）
    user_input: str                                   # 当前用户输入
    conversation_id: str                              # 会话ID
    user_id: str                                      # 用户ID

    # 路由与风险评估
    risk_assessment: RiskAssessment                   # 分诊评估结果
    next_agent: str                                   # 下一个要路由到的智能体

    # RAG 检索结果
    retrieved_context: list[str]                      # 检索到的相关文档片段

    # 工具调用结果
    tool_results: dict                                # 工具调用返回的额外数据

    # 会话元数据
    turn_count: int                                   # 当前轮次
    is_crisis: bool                                   # 是否处于危机状态
