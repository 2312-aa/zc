"""分诊智能体：识别用户意图、风险分级"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from config import LLM_MODEL_NAME, LLM_BASE_URL, LLM_API_KEY, LLM_TEMPERATURE
from graph.state import ConversationState, RiskAssessment


def _get_llm():
    kwargs = {
        "model": LLM_MODEL_NAME,
        "temperature": LLM_TEMPERATURE,
        "api_key": LLM_API_KEY,
    }
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return ChatOpenAI(**kwargs)


TRIAGE_SYSTEM_PROMPT = """你是一名专业的心理分诊师。你的职责是：

1. **意图识别**：判断用户的主要意图类别：
   - general_chat: 日常倾诉、闲聊
   - seek_help: 主动寻求心理帮助
   - emotional_distress: 情绪困扰（焦虑、抑郁、失眠等）
   - crisis: 危机信号（自伤、自杀意念、严重创伤）
   - resource_request: 请求资源（热线、医院、文章等）

2. **风险评估**：根据以下标准评估风险等级：
   - low (0-0.3): 一般心理困扰，情绪波动正常
   - medium (0.3-0.6): 明显的情绪困扰，需要关注
   - high (0.6-0.8): 严重心理问题，需要专业干预
   - crisis (0.8-1.0): 紧急危机，需要立即干预

**关键危机信号**：
- 提及自杀、自伤、不想活了、结束生命
- 严重自责、绝望感
- 提及具体的自伤计划
- 近期重大创伤事件

请以 JSON 格式输出评估结果：
```json
{{
  "risk_level": "low/medium/high/crisis",
  "risk_score": 0.0-1.0,
  "intent": "意图类别",
  "reasoning": "判断理由"
}}
```
"""


def triage_node(state: ConversationState) -> dict:
    """分诊节点：分析用户输入，输出风险评估"""
    llm = _get_llm()
    user_input = state.get("user_input", "")

    messages = [
        SystemMessage(content=TRIAGE_SYSTEM_PROMPT),
        HumanMessage(content=f"请评估以下用户输入：\n\n{user_input}"),
    ]

    response = llm.invoke(messages)
    content = response.content

    # 解析 LLM 返回的 JSON
    import json
    try:
        # 尝试从 markdown 代码块中提取 JSON
        if "```json" in content:
            json_str = content.split("```json")[1].split("```")[0].strip()
        elif "```" in content:
            json_str = content.split("```")[1].split("```")[0].strip()
        else:
            json_str = content.strip()
        assessment_data = json.loads(json_str)
        assessment = RiskAssessment(**assessment_data)
    except Exception:
        # 解析失败时使用默认低风险
        assessment = RiskAssessment(
            risk_level="low",
            risk_score=0.1,
            intent="general_chat",
            reasoning="自动评估降级：LLM输出解析失败",
        )

    # 确定路由
    is_crisis = assessment.risk_level in ("crisis", "high")
    if assessment.risk_level == "crisis":
        next_agent = "crisis"
    elif assessment.risk_level == "high":
        next_agent = "crisis"
    elif assessment.intent == "resource_request":
        next_agent = "resource"
    elif assessment.intent in ("seek_help", "emotional_distress"):
        next_agent = "counseling"
    else:
        next_agent = "counseling"

    return {
        "risk_assessment": assessment,
        "next_agent": next_agent,
        "is_crisis": is_crisis,
    }


# 兼容 LangGraph 直接引用
triage_agent = triage_node
