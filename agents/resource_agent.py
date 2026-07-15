"""资源推荐智能体：文章、热线、医院等资源"""
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
        "temperature": LLM_TEMPERATURE,
        "api_key": LLM_API_KEY,
    }
    if LLM_BASE_URL:
        kwargs["base_url"] = LLM_BASE_URL
    return ChatOpenAI(**kwargs)


RESOURCE_SYSTEM_PROMPT = """你是一位心理健康资源推荐助手。你帮助用户找到合适的心理健康资源，包括文章、热线电话、医院和专业服务。

## 推荐原则

1. **需求匹配**：根据用户的具体需求推荐最相关的资源
2. **分层推荐**：从自助资源到专业帮助，逐步递进
3. **信息准确**：只推荐经过验证的资源
4. **温暖引导**：用鼓励性的语言引导用户使用资源

## 推荐类别

### 自助资源
- 心理健康文章和书籍
- 冥想与正念应用
- 自助工作表（CBT思维记录等）

### 在线支持
- 心理健康社区和论坛
- 在线咨询平台
- 心理健康App

### 专业帮助
- 心理咨询热线
- 精神卫生中心
- 心理咨询机构

### 危机资源（高风险时必须推荐）
- 24小时心理危机热线
- 急诊精神科

## 已知危机热线
{hotlines}

## 注意事项
- 根据用户的风险等级调整推荐力度
- 高风险用户优先推荐专业和危机资源
- 提供具体可操作的信息
- 鼓励用户迈出寻求帮助的第一步
"""


def resource_node(state: ConversationState) -> dict:
    """资源推荐节点：为用户推荐合适的心理健康资源"""
    llm = _get_llm()
    user_input = state.get("user_input", "")
    risk_assessment = state.get("risk_assessment")
    retrieved_context = state.get("retrieved_context", [])

    # 格式化热线信息
    hotlines_text = "\n".join([f"  - {h['name']}: {h['phone']}" for h in CRISIS_HOTLINES])

    system_content = RESOURCE_SYSTEM_PROMPT.format(hotlines=hotlines_text)
    if risk_assessment:
        system_content += f"\n\n【用户风险等级】{risk_assessment.risk_level}"

    # RAG 上下文
    if retrieved_context:
        context_text = "\n\n【相关资料】\n" + "\n---\n".join(retrieved_context)
        system_content += context_text

    messages = [
        SystemMessage(content=system_content),
        HumanMessage(content=user_input),
    ]

    response = llm.invoke(messages)

    return {
        "messages": [AIMessage(content=response.content)],
        "turn_count": state.get("turn_count", 0) + 1,
    }


# 兼容 LangGraph
resource_agent = resource_node
