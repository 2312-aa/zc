"""
settings.py — 路径、切片、检索数量、存储路径静态常量配置
所有可变参数统一从环境变量读取，禁止硬编码
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# 加载.env配置
load_dotenv(override=True)

# ============================================================
# 项目根目录（以本文件所在目录的上一级为基准）
# ============================================================
PROJECT_ROOT = Path(__file__).resolve().parent.parent

# ============================================================
# 存储路径配置
# ============================================================
VECTOR_DB_PATH = os.getenv("VECTOR_DB_PATH", "./storage/chroma_vector")
UPLOAD_FILE_PATH = os.getenv("UPLOAD_FILE_PATH", "./storage/source_upload")
CHAT_HISTORY_PATH = os.getenv("CHAT_HISTORY_PATH", "./storage/chat_record")

# 转换为绝对路径
VECTOR_DB_PATH = str(PROJECT_ROOT / VECTOR_DB_PATH) if not os.path.isabs(VECTOR_DB_PATH) else VECTOR_DB_PATH
UPLOAD_FILE_PATH = str(PROJECT_ROOT / UPLOAD_FILE_PATH) if not os.path.isabs(UPLOAD_FILE_PATH) else UPLOAD_FILE_PATH
CHAT_HISTORY_PATH = str(PROJECT_ROOT / CHAT_HISTORY_PATH) if not os.path.isabs(CHAT_HISTORY_PATH) else CHAT_HISTORY_PATH

# ============================================================
# 文本切片参数
# ============================================================
CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "800"))
CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "150"))

# ============================================================
# 检索参数
# ============================================================
RETRIEVE_TOP_K = int(os.getenv("RETRIEVE_TOP_K", "6"))
RETRIEVE_TOP_N = int(os.getenv("RETRIEVE_TOP_N", "3"))
SIMILARITY_THRESHOLD = float(os.getenv("SIMILARITY_THRESHOLD", "0.45"))

# ============================================================
# 支持的文件格式
# ============================================================
SUPPORTED_EXTENSIONS = {".pdf", ".txt", ".md", ".docx", ".xlsx", ".xls"}

# ============================================================
# Ollama服务配置
# ============================================================
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://127.0.0.1:11434")

# ============================================================
# Chroma集合名称
# ============================================================
CHROMA_COLLECTION_NAME = "rag_knowledge_base"
