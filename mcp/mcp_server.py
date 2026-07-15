"""启动轻量 MCP 服务器，提供心理健康工具和资源"""
import json
import asyncio
from pathlib import Path

from mcp.server import Server
from mcp.server.sse import SseServerTransport
from mcp.types import Tool, TextContent

import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import MCP_HOST, MCP_PORT

# 加载 MCP 配置
CONFIG_PATH = Path(__file__).parent / "mcp_config.json"


def load_config():
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


# 创建 MCP 服务器
server = Server("mental-health-mcp")


@server.list_tools()
async def list_tools():
    """列出所有可用工具"""
    config = load_config()
    tools = []
    for t in config.get("tools", []):
        tools.append(Tool(
            name=t["name"],
            description=t["description"],
            inputSchema=t.get("parameters", {"type": "object", "properties": {}}),
        ))
    return tools


@server.call_tool()
async def call_tool(name: str, arguments: dict):
    """处理工具调用"""
    config = load_config()

    # 查找工具
    tool_config = None
    for t in config.get("tools", []):
        if t["name"] == name:
            tool_config = t
            break

    if not tool_config:
        return [TextContent(type="text", text=f"工具 '{name}' 不存在")]

    # 呼吸练习
    if name == "breathing_exercise":
        exercise_type = arguments.get("exercise_type", "478_breathing")
        duration = arguments.get("duration_minutes", 5)
        exercises = {
            "478_breathing": "4-7-8 呼吸法：吸气4秒，屏息7秒，呼气8秒",
            "box_breathing": "箱式呼吸：吸气4秒，屏息4秒，呼气4秒，屏息4秒",
            "deep_breathing": "腹式深呼吸：缓慢深吸气5秒，缓慢呼气5秒",
        }
        instruction = exercises.get(exercise_type, exercises["478_breathing"])
        return [TextContent(
            type="text",
            text=f"开始 {instruction}，建议练习 {duration} 分钟。\n\n"
                 f"请找一个舒适的姿势，闭上眼睛，让我们开始...\n\n"
                 f"1. 先自然呼吸几次，放松身体\n"
                 f"2. 按照上述节奏进行呼吸\n"
                 f"3. 注意力集中在呼吸上\n"
                 f"4. 如果走神了，轻轻把注意力拉回来\n"
                 f"5. 完成后，慢慢恢复正常呼吸",
        )]

    # 情绪追踪
    if name == "mood_tracker":
        score = arguments.get("mood_score", 5)
        label = arguments.get("mood_label", "")
        note = arguments.get("note", "")
        return [TextContent(
            type="text",
            text=f"已记录情绪状态：\n- 评分: {score}/10\n- 情绪: {label}\n- 备注: {note or '无'}\n\n"
                 f"持续记录情绪可以帮助你更好地了解自己。",
        )]

    # 接地练习
    if name == "grounding_exercise":
        step = arguments.get("step", "start")
        steps = {
            "start": "让我们开始 5-4-3-2-1 接地练习，帮助你回到当下。\n\n请看周围，说出你看到的 5 样东西...",
            "see": "很好！现在，触摸 4 样你能感觉到的东西...",
            "touch": "继续，说出 3 种你能听到的声音...",
            "hear": "很好！现在，说出 2 种你能闻到的气味...",
            "smell": "最后，说出 1 种你能尝到的味道...",
            "taste": "太棒了！你已经完成了接地练习。注意一下现在的感受，你是否感觉更回到当下了？",
            "complete": "练习完成！如果仍然感到不安，可以随时重复这个练习。",
        }
        return [TextContent(type="text", text=steps.get(step, steps["start"]))]

    return [TextContent(type="text", text=f"工具 '{name}' 已调用，参数: {arguments}")]


async def run_mcp_server():
    """启动 MCP 服务器"""
    from starlette.applications import Starlette
    from starlette.routing import Mount, Route

    sse = SseServerTransport("/messages/")

    async def handle_sse(request):
        async with sse.connect_sse(
            request.scope, request.receive, request._send
        ) as streams:
            await server.run(
                streams[0], streams[1], server.create_initialization_options()
            )

    app = Starlette(
        routes=[
            Route("/sse", endpoint=handle_sse),
            Mount("/messages/", app=sse.handle_post_message),
        ]
    )

    import uvicorn
    config = uvicorn.Config(app, host=MCP_HOST, port=MCP_PORT)
    server_instance = uvicorn.Server(config)
    await server_instance.serve()


if __name__ == "__main__":
    import asyncio
    asyncio.run(run_mcp_server())
