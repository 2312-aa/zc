"""咨询智能体：心理疏导、CBT对话"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage, AIMessage

from config import LLM_MODEL_NAME, LLM_BASE_URL, LLM_API_KEY, LLM_TEMPERATURE
from graph.state import ConversationState


def _get_llm():
    kwargs = {
        "model": LLM_MODEL_NAME,
        "temperature": LLM_TEMPERATURE,
        "api_key": LLM_API_KEY,
    }
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return ChatOpenAI(**kwargs)


COUNSELING_SYSTEM_PROMPT = """你是一位温暖、专业、有同理心的心理咨询师。你擅长使用认知行为疗法（CBT）和共情倾听来帮助来访者。

## 核心原则

1. **共情优先**：首先理解和确认来访者的感受，不要急于给建议
2. **安全第一**：如果发现危机信号，立即引导至危机干预
3. **非评判态度**：接受来访者的所有感受，不做道德评判
4. **专业边界**：明确你是AI助手，不能替代专业心理咨询

## 对话策略

### 日常倾诉
- 倾听、共情、确认感受
- "听起来你现在感到..." / "我能理解这种感觉..."

### 情绪困扰
- 使用CBT技术探索认知模式
- 帮助识别自动思维和认知扭曲
- "你当时想到了什么？" / "有没有其他的解释？"
- 认知重构：帮助找到更平衡的思维方式

### 行为激活
- 鼓励小步骤行动
- "如果你愿意的话，我们可以试着..."

### 正念与放松
- 引导简单呼吸练习
- 身体扫描放松

## 注意事项
- 回复简洁温暖，避免过长
- 适时使用开放式问题
- 关注来访者的资源和优势
- 如果检测到危机信号，提示需要转接危机干预
"""


def counseling_node(state: ConversationState) -> dict:
    """咨询节点：进行心理疏导对话"""
    llm = _get_llm()
    user_input = state.get("user_input", "")
    risk_assessment = state.get("risk_assessment")
    retrieved_context = state.get("retrieved_context", [])
    history_messages = state.get("messages", [])

    # 构建 RAG 上下文
    context_text = ""
    if retrieved_context:
        context_text = "\n\n【参考资料】\n" + "\n---\n".join(retrieved_context)

    # 构建消息列表
    system_content = COUNSELING_SYSTEM_PROMPT
    if risk_assessment:
        system_content += f"\n\n【风险评估】等级: {risk_assessment.risk_level}, 意图: {risk_assessment.intent}"
    if context_text:
        system_content += context_text

    messages = [SystemMessage(content=system_content)]

    # 添加历史消息（最近10轮）
    recent_history = history_messages[-20:] if len(history_messages) > 20 else history_messages
    messages.extend(recent_history)

    # 添加当前用户输入
    messages.append(HumanMessage(content=user_input))

    response = llm.invoke(messages)

    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state.get("turn_count", 0) + 1,
    }


# 兼容 LangGraph
counseling_agent = counseling_node
