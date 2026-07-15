"""知识库文档加载与入库脚本"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

import os
from pathlib import Path
from langchain_community.document_loaders import (
    TextLoader,
    PyMuPDFLoader,
    UnstructuredMarkdownLoader,
    DirectoryLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

from config import KNOWLEDGE_DIR, CHROMA_PERSIST_DIR, RAG_CHUNK_SIZE, RAG_CHUNK_OVERLAP
from rag.vector_store import get_vector_store


def _get_loader_for_file(file_path: Path):
    """根据文件扩展名选择加载器"""
    suffix = file_path.suffix.lower()
    if suffix == ".pdf":
        return PyMuPDFLoader(str(file_path))
    elif suffix == ".md":
        # 使用 TextLoader 加载 Markdown，避免依赖 unstructured
        return TextLoader(str(file_path), encoding="utf-8")
    elif suffix in (".txt", ".csv"):
        return TextLoader(str(file_path), encoding="utf-8")
    else:
        return TextLoader(str(file_path), encoding="utf-8")


def load_documents(directory: str = None) -> list:
    """从目录加载所有文档"""
    doc_dir = Path(directory) if directory else KNOWLEDGE_DIR
    if not doc_dir.exists():
        print(f"知识库目录不存在: {doc_dir}")
        return []

    all_docs = []
    for file_path in doc_dir.rglob("*"):
        if file_path.is_file() and file_path.suffix.lower() in (".txt", ".md", ".pdf", ".csv"):
            try:
                loader = _get_loader_for_file(file_path)
                docs = loader.load()
                for doc in docs:
                    doc.metadata["source_file"] = str(file_path.name)
                all_docs.extend(docs)
                print(f"已加载: {file_path.name} ({len(docs)} 条)")
            except Exception as e:
                print(f"加载失败 {file_path.name}: {e}")

    return all_docs


def split_documents(documents: list, chunk_size: int = None, chunk_overlap: int = None) -> list:
    """文档切分"""
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size or RAG_CHUNK_SIZE,
        chunk_overlap=chunk_overlap or RAG_CHUNK_OVERLAP,
        separators=["\n\n", "\n", "。", "！", "？", ".", " ", ""],
        length_function=len,
    )
    chunks = text_splitter.split_documents(documents)
    print(f"文档切分: {len(documents)} 篇 -> {len(chunks)} 块")
    return chunks


def load_knowledge_to_vector_store(directory: str = None):
    """加载知识库文档并写入向量库"""
    print("开始加载知识库...")
    documents = load_documents(directory)
    if not documents:
        print("未找到任何文档，跳过入库。")
        return

    chunks = split_documents(documents)
    print(f"正在写入 ChromaDB 向量库 ({len(chunks)} 块)...")

    vector_store = get_vector_store()
    vector_store.add_documents(chunks)

    print("知识库入库完成！")


if __name__ == "__main__":
    load_knowledge_to_vector_store()
