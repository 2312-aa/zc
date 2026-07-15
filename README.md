# Local-Ollama-RAG-System

## 基于 **Streamlit + Ollama** 的纯本地离线RAG知识库问答系统
适合作为本地知识库问答与 RAG 检索增强的实战项目
- 在网页端上传 `pdf/txt/md/docx/excel` 文件，自动切分后写入 Chroma 向量库
- 在网页端以聊天形式提问，基于知识库内容进行检索增强回答（RAG）
- 支持 **向量相似度过滤**、**多轮对话**、**溯源展示**、**MD5去重**
- 技术栈：Python / Streamlit / LangChain / Chroma / Ollama / nomic-embed-text / qwen:7b

---

## ✨ 功能一览

### 1) 知识库管理服务（Upload）
- Streamlit 页面上传文件，支持 pdf / txt / md / docx / excel 五种格式
- 自动读取文本内容，清洗乱码、多余换行空格
- 根据配置进行分段（RecursiveCharacterTextSplitter），支持自定义 chunk_size 与 chunk_overlap
- 写入 Chroma 向量库（本地持久化）
- 使用 **MD5 去重**：相同文件不重复入库
- 支持按文档名删除向量片段、一键清空知识库
- 大文件后台线程异步上传，页面不阻塞，附带进度提示

### 2) 智能问答服务（RAG Chat）
- Streamlit Chat UI，支持多轮连续问答
- 完整 RAG 链路：`用户Query → 向量召回Top-K → 相似度过滤Top-N → 拼接上下文+历史 → LLM生成答案`
- 支持 **溯源展示**：回答底部折叠面板展示文档来源、相似度分数、原文片段
- 支持 **多会话管理**：新建/切换/删除会话，对话历史本地文件持久化
- 支持 **会话清空**：一键清空当前会话历史

### 3) 健壮性保障
- **启动校验**：自动检测 Ollama 服务是否运行，校验 Embedding 和 LLM 模型是否已拉取，缺失则弹窗提示修复命令
- **全局单例**：Embedding / LLM 模型全局唯一实例，Streamlit 刷新不重复创建
- **重试机制**：所有 Ollama 接口添加 tenacity 重试装饰器，最多重试 3 次
- **异常处理**：自定义业务异常，前端友好中文提示，不暴露原始堆栈
- **全局日志**：INFO / WARN / ERROR 分级日志，文件自动轮转

---

## 🧩 项目结构

```text
Local-Ollama-RAG-System/
├─ .env                      # Ollama服务、模型、业务参数配置
├─ .gitignore                # 屏蔽向量库、上传文件、日志、缓存、密钥
├─ main.py                   # 统一命令行启动入口，切换上传/聊天页面
├─ requirements.txt          # 全量Python依赖
├─ README.md                 # 完整部署、模型拉取、启动、排错文档
├─ config/
│  ├─ settings.py            # 路径、切片、检索数量、存储路径静态常量
│  └─ llm_emb_config.py      # LLM/Embedding模型配置、阈值参数
├─ core/                     # 底层核心能力层
│  ├─ file_parser.py         # 文档解析：pdf/txt/md/docx/excel
│  ├─ text_splitter.py       # 文本清洗、分段、重叠切片
│  ├─ ollama_embed_factory.py # 向量嵌入模型全局单例工厂
│  ├─ vector_base/
│  │  ├─ base_vector.py      # 向量存储抽象基类
│  │  └─ chroma_store.py     # Chroma持久化向量库实现
│  └─ rag_chain_builder.py   # 完整RAG链路：召回→过滤→问答组装
├─ service/                  # 业务服务层，UI仅调用该层接口
│  ├─ knowledge_service.py   # 文件上传、切片入库、文档删除、知识库管理
│  ├─ chat_service.py        # 多轮问答、上下文拼接、溯源信息整理
│  └─ history_service.py     # 对话历史增删改查、本地文件持久化
├─ ui/                       # Streamlit前端页面
│  ├─ upload_kb_page.py      # 知识库上传、文档管理页面
│  └─ chat_page.py           # 多轮对话问答页面
├─ utils/                    # 通用工具集
│  ├─ logger_util.py         # 全局分级日志（loguru）
│  ├─ file_util.py           # MD5文件去重、目录创建、文件格式校验
│  ├─ exception_util.py      # 自定义业务异常统一捕获
│  └─ ollama_check_util.py   # 启动校验Ollama服务+模型是否就绪
└─ storage/                  # 自动生成持久化目录
   ├─ chroma_vector/          # Chroma向量数据库持久化文件
   ├─ source_upload/         # 原始上传文档存档
   └─ chat_record/           # 用户对话记录存储
```

---

## ✅ 环境准备

### 1) 安装 Ollama

```bash
# 访问官网下载安装
# https://ollama.com/download

# Linux 一键安装
curl -fsSL https://ollama.com/install.sh | sh

# macOS
brew install ollama

# 启动 Ollama 服务
ollama serve
```

### 2) 拉取必需模型

本项目使用 2 类模型：

| 模型类型 | 模型名称 | 用途 |
|---------|---------|------|
| 向量嵌入模型 | `nomic-embed-text` | 文本向量化、相似度召回 |
| 对话大模型 | `qwen:7b` | 根据知识库片段生成回答 |

```bash
# 向量嵌入模型
ollama pull nomic-embed-text

# 对话大模型
ollama pull qwen:7b
```

### 3) 安装 Python 依赖

```bash
# 建议使用虚拟环境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows

pip install -r requirements.txt -i https://pypi.tuna.tsinghua.edu.cn/simple
```
- 终端运行，建议虚拟环境加载，清华镜像源加速

---

## ⚙️ 配置说明

- `.env` 中包含核心配置，根据实际需要修改模型配置、chunk 大小、检索参数...
- 默认使用 `nomic-embed-text` 嵌入模型 + `qwen:7b` 对话模型
- 无需任何云端 API Key，全部本地运行

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| OLLAMA_BASE_URL | http://127.0.0.1:11434 | Ollama 服务地址 |
| OLLAMA_EMBED_MODEL | nomic-embed-text | 向量嵌入模型 |
| OLLAMA_LLM_MODEL | qwen:7b | 对话大模型 |
| RETRIEVE_TOP_K | 6 | 初始召回数量 |
| RETRIEVE_TOP_N | 3 | 最终返回片段数量 |
| SIMILARITY_THRESHOLD | 0.45 | 向量相似度阈值 |
| CHUNK_SIZE | 800 | 文本切片大小 |
| CHUNK_OVERLAP | 150 | 切片重叠字符数 |
| VECTOR_DB_PATH | ./storage/chroma_vector | 向量库持久化路径 |
| UPLOAD_FILE_PATH | ./storage/source_upload | 上传文件存档路径 |
| CHAT_HISTORY_PATH | ./storage/chat_record | 对话记录存储路径 |

---

## 🚀 快速运行

### 1) 启动知识库管理服务

```bash
python main.py --page upload
```
- 打开页面后上传 pdf / txt / md / docx / excel 文件，即可写入本地向量库
- 侧边栏查看知识库概览，支持按文档删除、一键清空

### 2) 启动智能问答服务（RAG Chat）

```bash
python main.py --page chat
```
- 输入问题后，会先检索知识库，过滤低相关片段，最终由模型综合回答
- 回答底部可展开溯源面板，查看文档来源、相似度分数、原文片段
- 侧边栏支持多会话管理、一键清空当前会话历史

启动后自动打开浏览器访问 `http://localhost:8501`

---

## 🛠 常见问题

### Q1：启动时提示"Ollama服务未启动"？
#### 可能原因：
- Ollama 服务未运行
#### 解决方案：
- 执行 `ollama serve` 启动服务
- 确认 `http://127.0.0.1:11434` 可访问

### Q2：启动时提示"缺少必要模型"？
#### 可能原因：
- 必需模型未拉取
#### 解决方案：
- 按提示执行对应的 `ollama pull <模型名>` 命令
- 使用 `ollama list` 查看本地已有模型

### Q3：上传文件后，聊天问答仍然"未找到相关内容"？
#### 可能原因：
- 向量相似度阈值 `SIMILARITY_THRESHOLD` 设置过高
- 切片参数不合适导致内容碎片化
#### 解决方案：
- 在 `.env` 中调低 `SIMILARITY_THRESHOLD`（如 0.3）
- 适当增大 `CHUNK_SIZE`（如 1200）

### Q4：回答显示较慢或超时？
#### 可能原因：
- 大模型推理速度取决于硬件配置
- 检索召回数量过多
#### 解决方案：
- 降低 `RETRIEVE_TOP_K` 减少召回数量
- 换用更轻量的模型（如 `qwen:4b`）
- 确保有足够的 GPU/CPU 资源

### Q5：上传文件后解析失败？
#### 可能原因：
- 文件损坏或编码不标准
- 不支持的文件格式
#### 解决方案：
- 检查文件完整性
- 确认文件格式在支持列表中（pdf/txt/md/docx/excel）

---

## ✨ 优化方向（仅供参考）
- 流式输出：接入 LangChain 的 Streaming 回调，逐 token 展示回答
- Rerank重排：接入Cross-Encoder重排模型（如bge-reranker），提升检索精度
- 多模态支持：增加图片/PDF扫描件OCR解析
- 向量库升级：Chroma → FAISS / Milvus，适配更大规模数据
- Agent 化：从 RAG 问答升级为工具调用 Agent，支持联网搜索、代码执行
- 多用户隔离：增加用户认证，知识库按用户隔离
- 前端升级：Streamlit → Gradio / Next.js，更灵活的交互体验
- 总之，这是一个基础但延展性很好的 RAG 项目，扩展升级 → 企业级 RAG → 功能插件 → Agent → AI产品

---

## 📄 License

- 本项目仅用于学习与交流，如需商用请自行补全安全、合规与授权相关内容。

---

## 🙌 致谢

- Ollama
- Streamlit
- LangChain
- Chroma / chromadb
- Qwen
- nomic-embed-text
