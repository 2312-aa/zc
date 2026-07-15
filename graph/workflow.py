"""多智能体路由与执行流程（LangGraph）"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langgraph.graph import StateGraph, END

from graph.state import ConversationState
from agents.triage_agent import triage_node
from agents.counseling_agent import counseling_node
from agents.crisis_agent import crisis_node
from agents.resource_agent import resource_node
from config import RAG_ENABLED

# RAG 检索延迟导入
RAG_AVAILABLE = False
retrieve_documents = None

def _init_rag():
    """延迟初始化 RAG"""
    global RAG_AVAILABLE, retrieve_documents
    if RAG_AVAILABLE:
        return
    if not RAG_ENABLED:
        return
    try:
        from rag.retriever import retrieve_documents as _retrieve
        retrieve_documents = _retrieve
        RAG_AVAILABLE = True
        print("RAG模块加载成功")
    except Exception as e:
        print(f"RAG模块加载失败: {e}")


def rag_retrieve_node(state: ConversationState) -> dict:
    """RAG 检索节点：根据用户输入检索相关知识"""
    # 延迟初始化
    _init_rag()

    if not RAG_AVAILABLE:
        return {"retrieved_context": []}

    user_input = state.get("user_input", "")
    if not user_input:
        return {"retrieved_context": []}

    try:
        docs = retrieve_documents(user_input, top_k=3)
        context_list = [doc["content"] for doc in docs]
        return {"retrieved_context": context_list}
    except Exception as e:
        print(f"RAG检索失败: {e}")
        return {"retrieved_context": []}


def route_after_triage(state: ConversationState) -> str:
    """分诊后的路由函数"""
    next_agent = state.get("next_agent", "counseling")
    if next_agent == "crisis":
        return "crisis"
    elif next_agent == "resource":
        return "resource"
    else:
        return "counseling"


def build_workflow() -> StateGraph:
    """构建多智能体工作流图

    流程：
    用户输入 -> RAG检索 -> 分诊评估 -> 路由 ->
        ├── 咨询智能体（低/中风险 + 日常/求助/情绪）
        ├── 危机干预智能体（高/危机风险）
        └── 资源推荐智能体（请求资源）
    -> END
    """
    graph = StateGraph(ConversationState)

    # 添加节点
    graph.add_node("rag_retrieve", rag_retrieve_node)
    graph.add_node("triage", triage_node)
    graph.add_node("counseling", counseling_node)
    graph.add_node("crisis", crisis_node)
    graph.add_node("resource", resource_node)

    # 设置入口
    graph.set_entry_point("rag_retrieve")

    # 边：RAG检索 -> 分诊
    graph.add_edge("rag_retrieve", "triage")

    # 条件边：分诊 -> 根据评估结果路由
    graph.add_conditional_edges(
        "triage",
        route_after_triage,
        {
            "counseling": "counseling",
            "crisis": "crisis",
            "resource": "resource",
        },
    )

    # 各智能体 -> 结束
    graph.add_edge("counseling", END)
    graph.add_edge("crisis", END)
    graph.add_edge("resource", END)

    return graph.compile()


# 全局工作流实例
workflow = build_workflow()
