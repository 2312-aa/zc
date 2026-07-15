"""
main.py — 统一命令行启动入口，切换上传/聊天页面
通过 --page 参数指定启动哪个Streamlit页面

启动命令：
  python main.py --page upload    # 知识库上传管理页
  python main.py --page chat      # 多轮对话问答页
"""
import os
# 限制OpenBLAS线程数，防止内存分配失败
os.environ.setdefault("OPENBLAS_NUM_THREADS", "1")
os.environ.setdefault("OMP_NUM_THREADS", "1")

import argparse
import subprocess
import sys


def main():
    parser = argparse.ArgumentParser(
        description="Local-Ollama-RAG-System 本地离线RAG知识库问答系统"
    )
    parser.add_argument(
        "--page",
        type=str,
        choices=["upload", "chat"],
        required=True,
        help="选择启动页面: upload=知识库上传管理页, chat=多轮对话问答页",
    )
    args = parser.parse_args()

    # 获取项目根目录（main.py所在目录）
    project_dir = os.path.dirname(os.path.abspath(__file__))

    # 页面配置
    if args.page == "upload":
        page_title = "📚 知识库管理"
        page_icon = "📚"
        import_func = "render_upload_kb_page"
        import_module = "ui.upload_kb_page"
    else:
        page_title = "💬 智能问答"
        page_icon = "💬"
        import_func = "render_chat_page"
        import_module = "ui.chat_page"

    # 构建临时Streamlit启动脚本
    runner_script = os.path.join(project_dir, "_streamlit_runner.py")

    runner_code = f'''"""临时启动脚本 - 由main.py自动生成"""
import sys
sys.path.insert(0, r"{project_dir}")

import streamlit as st

# 页面配置（必须在最前面）
st.set_page_config(
    page_title="{page_title}",
    page_icon="{page_icon}",
    layout="wide",
)

# 启动前校验Ollama服务与模型
try:
    from utils.ollama_check_util import startup_check
    startup_check()
except Exception as e:
    st.error(f"⚠️ 系统启动校验失败: {{e}}")
    st.info("请按以下步骤修复：\\n1. 确保Ollama服务已启动\\n2. 确保所需模型已拉取")
    st.stop()

# 渲染对应页面
from {import_module} import {import_func}
{import_func}()
'''

    with open(runner_script, "w", encoding="utf-8") as f:
        f.write(runner_code)

    try:
        # 启动Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run",
            runner_script,
            "--server.port=8501",
            "--server.headless=true",
            "--browser.gatherUsageStats=false",
        ]
        subprocess.run(cmd, cwd=project_dir)
    finally:
        # 清理临时启动脚本
        if os.path.exists(runner_script):
            os.remove(runner_script)


if __name__ == "__main__":
    main()
