"""危机干预智能体：高风险/危机情况处理"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import LLM_MODEL_NAME, LLM_BASE_URL, LLM_API_KEY, LLM_TEMPERATURE, CRISIS_HOTLINES
from graph.state import ConversationState


def _get_llm():
    kwargs = {
        "model": LLM_MODEL_NAME,
        "temperature": 0.3,  # 危机场景降低随机性
        "api_key": LLM_API_KEY,
    }
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return ChatOpenAI(**kwargs)


def _format_hotlines():
    """格式化危机热线信息"""
    lines = []
    for h in CRISIS_HOTLINES:
        lines.append(f"  - {h['name']}: {h['phone']}")
    return "\n".join(lines)


CRISIS_SYSTEM_PROMPT = """你是一名专业的心理危机干预师。你正在处理一个高风险的心理危机情况。

## 核心原则

1. **立即稳定情绪**：优先建立安全感和连接感
2. **不评判、不惊慌**：保持冷静、稳定的态度
3. **确认安全**：评估当前安全状况
4. **绝不忽视**：任何危机信号都必须严肃对待
5. **专业转介**：明确需要专业帮助，提供热线信息

## 对话流程

### 第一步：建立连接
- "我在这里陪着你"
- "谢谢你愿意告诉我这些"
- "你的感受是真实的，也是重要的"

### 第二步：评估安全
- "你现在安全吗？"
- "你现在在哪里？身边有人吗？"
- 如果有自伤计划，需要紧急处理

### 第三步：稳定情绪
- 引导深呼吸
- 帮助回到当下（5-4-3-2-1接地技术）
- "能告诉我你现在看到的5样东西吗？"

### 第四步：提供资源
- 必须提供危机热线信息
- 建议寻求面对面专业帮助
- 如果可能，联系身边的信任的人

## 危机热线（必须提供）
{hotlines}

## 绝对禁止
- 不要说"想开点"等轻率话语
- 不要否定对方的感受
- 不要承诺你无法做到的事
- 不要离开对话或让对方等待
- 不要提供诊断
"""


def crisis_node(state: ConversationState) -> dict:
    """危机干预节点：处理高风险/危机情况"""
    llm = _get_llm()
    user_input = state.get("user_input", "")
    risk_assessment = state.get("risk_assessment")
    history_messages = state.get("messages", [])

    system_content = CRISIS_SYSTEM_PROMPT.format(hotlines=_format_hotlines())
    if risk_assessment:
        system_content += f"\n\n【风险评估】等级: {risk_assessment.risk_level}, 评分: {risk_assessment.risk_score}, 理由: {risk_assessment.reasoning}"

    messages = [SystemMessage(content=system_content)]
    recent_history = history_messages[-20:] if len(history_messages) > 20 else history_messages
    messages.extend(recent_history)
    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)

    # 危机情况始终附加热线信息提醒
    hotline_reminder = "\n\n---\n请记住，你不是独自一人。如果你感到不安全，请立即拨打：\n"
    for h in CRISIS_HOTLINES:
        hotline_reminder += f"- {h['name']}: **{h['phone']}**\n"

    final_content = response.content + hotline_reminder

    return {
        "messages": [AIMessage(content=final_content)],
        "is_crisis": True,
        "turn_count": state.get("turn_count", 0) + 1,
    }


# 兼容 LangGraph
crisis_agent = crisis_node
