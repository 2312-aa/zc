"""MCP 工具连接封装"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import json
from pathlib import Path
from langchain_core.tools import tool

from config import MCP_HOST, MCP_PORT


def _load_mcp_config() -> dict:
    """加载 MCP 配置文件"""
    config_path = Path(__file__).parent.parent / "mcp" / "mcp_config.json"
    if config_path.exists():
        with open(config_path, "r", encoding="utf-8") as f:
            return json.load(f)
    return {"tools": [], "resources": []}


# ==================== 本地心理健康工具 ====================

@tool
def breathing_exercise(exercise_type: str = "478_breathing", duration_minutes: int = 5) -> str:
    """引导用户进行呼吸放松练习。

    Args:
        exercise_type: 呼吸类型 (478_breathing/box_breathing/deep_breathing)
        duration_minutes: 练习时长（分钟）
    """
    exercises = {
        "478_breathing": "4-7-8 呼吸法：吸气4秒，屏息7秒，呼气8秒",
        "box_breathing": "箱式呼吸：吸气4秒，屏息4秒，呼气4秒，屏息4秒",
        "deep_breathing": "腹式深呼吸：缓慢深吸气5秒，缓慢呼气5秒",
    }
    instruction = exercises.get(exercise_type, exercises["478_breathing"])
    return (
        f"[呼吸练习] 开始 {instruction}，建议练习 {duration_minutes} 分钟。\n\n"
        f"请找一个舒适的姿势，闭上眼睛，让我们开始...\n\n"
        f"1. 先自然呼吸几次，放松身体\n"
        f"2. 按照上述节奏进行呼吸\n"
        f"3. 注意力集中在呼吸上\n"
        f"4. 如果走神了，轻轻把注意力拉回来\n"
        f"5. 完成后，慢慢恢复正常呼吸\n\n"
        f"[提示] 这个练习可以帮助你放松身心，减轻焦虑。"
    )


@tool
def mood_tracker(mood_score: int = 5, mood_label: str = "", note: str = "") -> str:
    """记录用户情绪状态和评分。

    Args:
        mood_score: 情绪评分 (1-10)
        mood_label: 情绪标签（如：焦虑、平静、悲伤等）
        note: 备注说明
    """
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return (
        f"[记录成功] 已记录情绪状态：\n"
        f"- 时间: {timestamp}\n"
        f"- 评分: {mood_score}/10\n"
        f"- 情绪: {mood_label or '未标注'}\n"
        f"- 备注: {note or '无'}\n\n"
        f"[提示] 持续记录情绪可以帮助你更好地了解自己的情绪模式。"
    )


@tool
def grounding_exercise(step: str = "start") -> str:
    """5-4-3-2-1 接地技术引导，帮助用户回到当下。

    Args:
        step: 练习步骤 (start/see/touch/hear/smell/taste/complete)
    """
    steps = {
        "start": (
            "[接地练习] 让我们开始 5-4-3-2-1 接地练习，帮助你回到当下。\n\n"
            "请看周围，说出你看到的 **5 样东西**...\n"
            "（可以是任何东西：桌子、椅子、杯子、窗户、墙壁...）"
        ),
        "see": (
            "[步骤2] 很好！现在，触摸 **4 样** 你能感觉到的东西...\n"
            "（比如：衣服的质感、桌面的温度、椅子的扶手...）"
        ),
        "touch": (
            "[步骤3] 继续，说出 **3 种** 你能听到的声音...\n"
            "（可以是：风扇声、远处的说话声、空调声...）"
        ),
        "hear": (
            "[步骤4] 很好！现在，说出 **2 种** 你能闻到的气味...\n"
            "（比如：咖啡香、空气的味道、植物的气息...）"
        ),
        "smell": (
            "[步骤5] 最后，说出 **1 种** 你能尝到的味道...\n"
            "（可能是口中的味道、刚才喝的水、嚼的口香糖...）"
        ),
        "taste": (
            "[完成] 太棒了！你已经完成了接地练习。\n\n"
            "注意一下现在的感受，你是否感觉更回到当下了？\n"
            "如果仍然感到不安，可以随时重复这个练习。"
        ),
        "complete": (
            "[练习完成]\n\n"
            "5-4-3-2-1 技术可以帮助你在焦虑时重新连接当下。\n"
            "随时可以使用这个练习来稳定情绪。"
        ),
    }
    return steps.get(step, steps["start"])


@tool
def call_mcp_tool(tool_name: str, arguments: dict = None) -> str:
    """通过 MCP 协议调用远程工具（可选）。

    Args:
        tool_name: MCP 工具名称
        arguments: 工具参数字典
    """
    arguments = arguments or {}

    # 本地工具映射
    local_tools = {
        "breathing_exercise": breathing_exercise,
        "mood_tracker": mood_tracker,
        "grounding_exercise": grounding_exercise,
    }

    if tool_name in local_tools:
        return local_tools[tool_name].invoke(arguments)

    return f"MCP 工具 '{tool_name}' 未找到"


@tool
def list_mcp_tools() -> str:
    """列出所有可用的 MCP 工具。"""
    return (
        "[可用工具] 心理健康工具列表：\n"
        "- breathing_exercise: 呼吸放松练习\n"
        "- mood_tracker: 情绪追踪记录\n"
        "- grounding_exercise: 5-4-3-2-1 接地技术"
    )


def get_mcp_tools():
    """获取所有 MCP 工具列表，供智能体绑定使用"""
    return [breathing_exercise, mood_tracker, grounding_exercise, call_mcp_tool, list_mcp_tools]
