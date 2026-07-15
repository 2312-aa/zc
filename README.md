<div align="center">
  <h1>Mental Health Agents</h1>
  <p><strong>AI 驱动的心理健康多智能体系统</strong></p>
  <p>
    <a href="#功能特性">功能特性</a> •
    <a href="#系统架构">系统架构</a> •
    <a href="#快速开始">快速开始</a> •
    <a href="#部署指南">部署指南</a> •
    <a href="#技术栈">技术栈</a>
  </p>
  <p>
    <img src="https://img.shields.io/badge/Python-3.10+-blue?logo=python" alt="Python">
    <img src="https://img.shields.io/badge/LangChain-0.3+-green?logo=langchain" alt="LangChain">
    <img src="https://img.shields.io/badge/Streamlit-1.30+-red?logo=streamlit" alt="Streamlit">
    <img src="https://img.shields.io/badge/ChromaDB-0.4+-purple" alt="ChromaDB">
    <img src="https://img.shields.io/badge/License-MIT-yellow" alt="License">
  </p>
</div>

---

## 📖 项目简介

**Mental Health Agents** 是一个基于 LangGraph 的心理健康智能助手系统，融合了 **多智能体协作**、**RAG 知识增强**、**风险评估**、**CBT 心理疏导** 等技术，为用户提供专业的心理支持服务。

### ✨ 核心亮点

- 🤖 **多智能体协作** - 分诊、咨询、危机干预、资源推荐四大多智能体协同工作
- 🧠 **智能风险评估** - 自动识别用户心理状态，进行风险分级（low/medium/high/crisis）
- 📚 **RAG 知识增强** - ChromaDB + Ollama/BGE 嵌入，专业知识库辅助回答
- 💬 **CBT 心理疏导** - 咨询智能体运用认知行为疗法进行专业心理辅导
- 🚨 **危机干预机制** - 高风险自动触发危机处理流程，附加热线资源
- 🔧 **MCP 工具集成** - 呼吸练习、情绪追踪、接地技术等心理健康工具
- 🗄️ **多轮对话存储** - SQLAlchemy + SQLite/PostgreSQL 持久化对话历史
- 🎨 **现代化界面** - Streamlit 构建的简洁友好聊天界面

---

## 🖼️ 界面预览

<details>
<summary>点击展开截图</summary>

### 主界面
![Chat Interface](docs/images/chat.png)

### 知识库管理
![Knowledge Base](docs/images/knowledge.png)

### 用户档案
![User Profile](docs/images/profile.png)

</details>

---

## 🏗️ 系统架构

```
┌─────────────────────────────────────────────────────────────────┐
│                    Frontend (Streamlit)                          │
│                  聊天界面 • 用户管理 • 知识库管理                  │
└─────────────────────────────┬───────────────────────────────────┘
                              │
┌─────────────────────────────▼───────────────────────────────────┐
│                   LangGraph Workflow                             │
│                 状态管理 • 条件路由 • 节点编排                     │
└─────────────────────────────┬───────────────────────────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        ▼                     ▼                     ▼
┌───────────────┐     ┌───────────────┐     ┌───────────────┐
│  RAG 检索节点  │     │   分诊智能体   │     │   MCP 工具    │
│ ─────────────│     │ ─────────────│     │ ─────────────│
│ • 向量检索    │     │ • 意图识别    │     │ • 呼吸练习    │
│ • 知识增强    │     │ • 风险评估    │     │ • 情绪追踪    │
└───────┬───────┘     └───────┬───────┘     │ • 接地技术    │
        │                     │             └───────────────┘
        │           ┌─────────┴─────────┐
        │           │    条件路由节点    │
        │           └─────────┬─────────┘
        │     ┌───────────────┼───────────────┐
        │     ▼               ▼               ▼
        │ ┌───────────┐ ┌───────────┐ ┌───────────┐
        │ │咨询智能体 │ │危机智能体 │ │资源智能体 │
        │ │──────────│ │──────────│ │──────────│
        │ │• CBT疏导 │ │• 稳定技术 │ │• 热线推荐 │
        │ │• 情绪支持 │ │• 热线信息 │ │• 文章推荐 │
        │ └───────────┘ └───────────┘ └───────────┘
        │         │             │             │
        └─────────┴─────────────┴─────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                   ChromaDB • SQLite • Ollama                    │
│               向量存储 • 对话存储 • 嵌入模型                      │
└─────────────────────────────────────────────────────────────────┘
```

### 智能体说明

| 智能体 | 职责 | 触发条件 |
|--------|------|----------|
| **分诊智能体** | 意图识别、风险评估 | 每次对话必经 |
| **咨询智能体** | CBT 心理疏导、情绪支持 | low/medium 风险 |
| **危机智能体** | 稳定技术、热线推荐 | high/crisis 风险 |
| **资源智能体** | 热线、文章、医院推荐 | resource_request 意图 |

---

## 🎯 功能特性

### 🧠 多智能体协作

基于 LangGraph 状态图实现智能体间协作：

```
用户输入 → RAG检索 → 分诊评估 → 条件路由 → 专业智能体响应
```

- **自动路由** - 根据风险评估结果自动分配智能体
- **状态传递** - 多轮对话上下文自动传递
- **并行处理** - RAG 检索与分诊可并行执行

### 📊 风险评估

四级风险分级体系：

| 等级 | 分数范围 | 处理方式 |
|------|----------|----------|
| `low` | 0-0.3 | 咨询智能体：日常倾诉、心理教育 |
| `medium` | 0.3-0.6 | 咨询智能体：CBT 对话、情绪支持 |
| `high` | 0.6-0.8 | 危机智能体：稳定技术 + 热线推荐 |
| `crisis` | 0.8-1.0 | 危机智能体：紧急干预 + 专业资源 |

**关键危机信号识别**：
- 提及自杀、自伤、不想活了
- 严重自责、绝望感
- 具体自伤计划
- 近期重大创伤事件

### 📚 RAG 知识增强

- **向量检索** - ChromaDB 存储专业知识库
- **嵌入模型** - 支持 Ollama 本地模型 / BGE 模型
- **知识库管理** - Web 界面一键加载文档

内置知识库：
- CBT 认知行为疗法指南
- 焦虑情绪应对指南
- 抑郁情绪自助指南
- 正念冥想入门指南

### 🔧 MCP 工具集成

心理健康辅助工具：

| 工具 | 说明 |
|------|------|
| `breathing_exercise` | 呼吸放松练习（4-7-8 呼吸法、箱式呼吸等） |
| `mood_tracker` | 情绪追踪记录 |
| `grounding_exercise` | 5-4-3-2-1 接地技术 |

---

## 🛠️ 技术栈

### 后端

| 技术 | 用途 |
|------|------|
| **Python 3.10+** | 主开发语言 |
| **LangChain** | LLM 应用框架 |
| **LangGraph** | 多智能体状态编排 |
| **ChromaDB** | 向量数据库 |
| **SQLAlchemy** | ORM 数据库操作 |
| **SQLite/PostgreSQL** | 关系数据库 |
| **Pydantic** | 数据验证 |

### 前端

| 技术 | 用途 |
|------|------|
| **Streamlit** | Web 框架 |
| **Python** | 前端逻辑 |

### 嵌入模型

| 模型 | 说明 |
|------|------|
| **Ollama** | 本地部署，支持 qwen3-embedding |
| **BGE** | 本地模型，BAAI/bge-small-zh-v1.5 |

### LLM 支持

- OpenAI (GPT-4o, GPT-4o-mini)
- 阿里云百炼 (qwen-plus, qwen-max)
- DeepSeek (deepseek-chat)
- 智谱 AI (GLM-4)
- Ollama 本地模型
- 其他 OpenAI 兼容 API

---

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Ollama (可选，用于本地嵌入模型)

### 1. 克隆项目

```bash
git clone https://github.com/your-username/mental_health_agents.git
cd mental_health_agents
```

### 2. 安装依赖

```bash
# 创建虚拟环境
python -m venv venv

# 激活虚拟环境
.\venv\Scripts\activate    # Windows
# source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt
```

### 3. 配置环境

编辑 `config.py`，配置你的 LLM API：

```python
# LLM 配置
LLM_MODEL_NAME = "qwen-plus"
LLM_BASE_URL = "https://dashscope.aliyuncs.com/compatible-mode/v1"
LLM_API_KEY = "your-api-key-here"
```

或使用环境变量：

```bash
export LLM_MODEL_NAME="qwen-plus"
export LLM_BASE_URL="https://dashscope.aliyuncs.com/compatible-mode/v1"
export LLM_API_KEY="your-api-key"
```

### 4. 配置嵌入模型（可选）

#### 使用 Ollama 本地嵌入模型

```bash
# 安装 Ollama
# 参考: https://ollama.ai

# 拉取嵌入模型
ollama pull qwen3-embedding:0.6b
```

修改 `config.py`：

```python
EMBEDDING_PROVIDER = "ollama"
EMBEDDING_MODEL_NAME = "qwen3-embedding:0.6b"
EMBEDDING_BASE_URL = "http://localhost:11434"
RAG_ENABLED = True
```

### 5. 加载知识库

```bash
python -c "
import sys
sys.path.insert(0, '.')
from rag.knowledge_loader import load_knowledge_to_vector_store
load_knowledge_to_vector_store()
"
```

### 6. 启动服务

```bash
streamlit run app.py
```

### 7. 访问服务

- 前端界面: http://localhost:8501

---

## 📦 项目结构

```
mental_health_agents/
├── app.py                      # Streamlit 前端入口
├── config.py                   # 全局配置
├── requirements.txt            # Python 依赖
│
├── agents/                     # 智能体模块
│   ├── triage_agent.py         # 分诊智能体
│   ├── counseling_agent.py     # 咨询智能体
│   ├── crisis_agent.py         # 危机干预智能体
│   └── resource_agent.py       # 资源推荐智能体
│
├── graph/                      # LangGraph 工作流
│   ├── state.py                # 状态定义
│   └── workflow.py             # 工作流编排
│
├── rag/                        # RAG 模块
│   ├── vector_store.py         # 向量数据库
│   ├── retriever.py            # 检索器
│   └── knowledge_loader.py     # 知识库加载
│
├── tools/                      # 工具模块
│   ├── database_tools.py       # 数据库工具
│   ├── external_api_tools.py   # 外部 API
│   └── mcp_tools.py            # MCP 工具
│
├── mcp/                        # MCP 服务
│   ├── mcp_server.py           # MCP 服务器
│   └── mcp_config.json         # MCP 配置
│
├── db/                         # 数据库模块
│   ├── models.py               # 数据模型
│   └── session.py              # 会话管理
│
├── data/                       # 数据目录
│   ├── knowledge/              # 知识库文档
│   ├── chroma_db/              # 向量存储
│   └── mental_health.db        # SQLite 数据库
│
└── README.md                   # 本文件
```

---

## 📖 部署指南

### 本地部署

```bash
# 安装依赖
pip install -r requirements.txt

# 配置 API Key
export LLM_API_KEY="your-key"

# 启动服务
streamlit run app.py --server.port 8501
```

### Docker 部署

```bash
# 构建镜像
docker build -t mental-health-agents .

# 运行容器
docker run -d \
  -p 8501:8501 \
  -e LLM_API_KEY=your-key \
  -e LLM_BASE_URL=https://api.openai.com/v1 \
  mental-health-agents
```

---

## 🔧 配置说明

完整配置项见 `config.py`，主要配置：

### LLM 配置

| 配置项 | 说明 | 必须 |
|--------|------|------|
| `LLM_MODEL_NAME` | 模型名称 | ✅ |
| `LLM_BASE_URL` | API 地址 | ✅ |
| `LLM_API_KEY` | API 密钥 | ✅ |
| `LLM_TEMPERATURE` | 温度参数 | ❌ |

### RAG 配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `RAG_ENABLED` | 是否启用 | `true` |
| `RAG_TOP_K` | 检索数量 | `5` |
| `RAG_CHUNK_SIZE` | 切分大小 | `500` |

### 嵌入模型配置

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `EMBEDDING_PROVIDER` | 提供商 | `ollama` |
| `EMBEDDING_MODEL_NAME` | 模型名称 | `qwen3-embedding:0.6b` |

---

## 📝 添加知识库

将文档放入 `data/knowledge/` 目录，支持：

| 格式 | 说明 |
|------|------|
| `.md` | Markdown 文档 |
| `.txt` | 纯文本 |
| `.pdf` | PDF 文档 |

然后在 Web 界面点击「加载知识库」。

---

## 🗺️ 路线图

- [x] 基础架构搭建
- [x] 多智能体协作
- [x] 风险评估系统
- [x] RAG 知识增强
- [x] CBT 心理疏导
- [x] 危机干预机制
- [x] MCP 工具集成
- [x] Streamlit 前端

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request！

1. Fork 本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 提交 Pull Request

---

## 📄 许可证

本项目采用 [MIT License](LICENSE) 开源许可证。

---

## ⚠️ 免责声明

本系统仅供心理支持辅助使用，不能替代专业心理咨询或医疗诊断。如有严重心理问题，请及时寻求专业帮助。

**全国心理援助热线**：
- 北京心理危机研究与干预中心：010-82951332
- 全国希望24热线：400-161-9995
- 生命热线：400-821-1215

---

## 🙏 致谢

- [LangChain](https://langchain.com) - LLM 应用框架
- [LangGraph](https://langchain-ai.github.io/langgraph/) - 多智能体编排
- [ChromaDB](https://www.trychroma.com) - 向量数据库
- [Streamlit](https://streamlit.io) - 前端框架
- [Ollama](https://ollama.ai) - 本地模型部署

---

<div align="center">
  <p>如果这个项目对你有帮助，请给一个 ⭐ Star 支持一下！</p>
</div>