"""ChromaDB 向量库初始化与嵌入模型"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.vectorstores import Chroma
from config import (
    EMBEDDING_PROVIDER,
    EMBEDDING_MODEL_NAME,
    EMBEDDING_BASE_URL,
    CHROMA_PERSIST_DIR,
    CHROMA_COLLECTION_NAME,
)


def get_embedding_model():
    """获取嵌入模型（支持 Ollama）"""
    if EMBEDDING_PROVIDER == "ollama":
        from langchain_community.embeddings import OllamaEmbeddings
        return OllamaEmbeddings(
            model=EMBEDDING_MODEL_NAME,
            base_url=EMBEDDING_BASE_URL,
        )
    else:
        from langchain_community.embeddings import HuggingFaceEmbeddings
        return HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL_NAME,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )


def get_vector_store():
    """获取或创建 ChromaDB 向量存储"""
    embeddings = get_embedding_model()
    vector_store = Chroma(
        collection_name=CHROMA_COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=str(CHROMA_PERSIST_DIR),
    )
    return vector_store
