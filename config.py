"""全局配置：模型名、路径、数据库URL等"""
import os
from pathlib import Path

# ==================== 项目路径 ====================
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
KNOWLEDGE_DIR = DATA_DIR / "knowledge"
CHROMA_PERSIST_DIR = DATA_DIR / "chroma_db"

# 确保目录存在
DATA_DIR.mkdir(exist_ok=True)
KNOWLEDGE_DIR.mkdir(exist_ok=True)
CHROMA_PERSIST_DIR.mkdir(exist_ok=True)

# ==================== LLM 配置 ====================
# 支持 OpenAI 兼容接口（可切换为 DeepSeek、智谱等）
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")
LLM_MODEL_NAME = os.getenv("LLM_MODEL_NAME", "qwen-plus")
LLM_BASE_URL = os.getenv("LLM_BASE_URL", "https://dashscope.aliyuncs.com/compatible-mode/v1")
LLM_API_KEY = os.getenv("LLM_API_KEY", "your-api-key-here")
LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

# ==================== 数据库配置 ====================
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR / 'mental_health.db'}")

# ==================== Embedding 配置 ====================
EMBEDDING_PROVIDER = os.getenv("EMBEDDING_PROVIDER", "ollama")  # ollama / huggingface
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "qwen3-embedding:0.6b")
EMBEDDING_BASE_URL = os.getenv("EMBEDDING_BASE_URL", "http://localhost:11434")
EMBEDDING_DEVICE = os.getenv("EMBEDDING_DEVICE", "cpu")
CHROMA_COLLECTION_NAME = "mental_health_knowledge"

# ==================== RAG 配置 ====================
RAG_ENABLED = os.getenv("RAG_ENABLED", "true").lower() == "true"  # 已启用
RAG_TOP_K = int(os.getenv("RAG_TOP_K", "5"))
RAG_CHUNK_SIZE = int(os.getenv("RAG_CHUNK_SIZE", "500"))
RAG_CHUNK_OVERLAP = int(os.getenv("RAG_CHUNK_OVERLAP", "50"))

# ==================== MCP 配置 ====================
MCP_HOST = os.getenv("MCP_HOST", "localhost")
MCP_PORT = int(os.getenv("MCP_PORT", "8900"))

# ==================== 风险分级阈值 ====================
RISK_LEVELS = {
    "low": "低风险 - 一般心理困扰",
    "medium": "中风险 - 需要专业关注",
    "high": "高风险 - 需要危机干预",
    "crisis": "紧急危机 - 立即干预"
}

# ==================== 危机热线 ====================
CRISIS_HOTLINES = [
    {"name": "全国24小时心理危机干预热线", "phone": "400-161-9995"},
    {"name": "北京心理危机研究与干预中心", "phone": "010-82951332"},
    {"name": "生命热线", "phone": "400-821-1215"},
    {"name": "希望24热线", "phone": "400-161-9995"},
]
