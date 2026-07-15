"""
chroma_store.py — Chroma持久化向量库实现
基于ChromaDB实现向量存储的增、删、查操作
"""
from typing import List, Optional

import chromadb
from chromadb.config import Settings as ChromaSettings

from core.vector_base.base_vector import BaseVectorStore
from core.ollama_embed_factory import get_embed_instance
from utils.logger_util import get_logger
from utils.exception_util import VectorStoreError
from config.settings import VECTOR_DB_PATH, CHROMA_COLLECTION_NAME

logger = get_logger("ChromaStore")


class ChromaVectorStore(BaseVectorStore):
    """ChromaDB持久化向量库实现"""

    def __init__(
        self,
        persist_directory: str = VECTOR_DB_PATH,
        collection_name: str = CHROMA_COLLECTION_NAME,
    ):
        """
        初始化ChromaDB向量库
        Args:
            persist_directory: 持久化存储目录
            collection_name: 集合名称
        """
        try:
            self._client = chromadb.PersistentClient(
                path=persist_directory,
            )
            self._collection = self._client.get_or_create_collection(
                name=collection_name,
                metadata={"hnsw:space": "cosine"},
            )
            self._embeddings = get_embed_instance()
            logger.info(f"ChromaDB初始化成功: 目录={persist_directory}, 集合={collection_name}")
        except Exception as e:
            raise VectorStoreError(
                "ChromaDB向量库初始化失败",
                detail=str(e)
            )

    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        批量添加文本到向量库
        使用Ollama Embedding模型生成向量，批量入库
        """
        if not texts:
            logger.warning("添加文本为空，跳过")
            return []

        try:
            # 批量生成向量嵌入
            embeddings = self._embeddings.embed_documents(texts)

            # 生成唯一ID
            ids = [f"doc_{self._collection.count() + i}" for i in range(len(texts))]

            # 确保metadata格式正确（ChromaDB要求值为str/int/float/bool）
            safe_metadatas = []
            if metadatas:
                for meta in metadatas:
                    safe_meta = {}
                    for k, v in meta.items():
                        safe_meta[k] = str(v) if v is not None else ""
                    safe_metadatas.append(safe_meta)
            else:
                safe_metadatas = [{}] * len(texts)

            # 批量添加到ChromaDB
            self._collection.add(
                ids=ids,
                embeddings=embeddings,
                documents=texts,
                metadatas=safe_metadatas,
            )

            logger.info(f"批量添加向量完成: 文本数={len(texts)}, ID范围={ids[0]}~{ids[-1]}")
            return ids

        except Exception as e:
            raise VectorStoreError(
                f"批量添加向量失败，文本数={len(texts)}",
                detail=str(e)
            )

    def similarity_search(
        self,
        query: str,
        top_k: int = 6,
    ) -> List[dict]:
        """
        向量相似度检索
        Returns格式: [{"text": str, "metadata": dict, "score": float}, ...]
        Chroma返回的距离是cosine distance，1-distance即为相似度
        """
        if not query.strip():
            logger.warning("查询文本为空")
            return []

        try:
            # 生成查询向量
            query_embedding = self._embeddings.embed_query(query)

            # ChromaDB相似度查询
            results = self._collection.query(
                query_embeddings=[query_embedding],
                n_results=min(top_k, self._collection.count()),
                include=["documents", "metadatas", "distances"],
            )

            # 整理结果
            search_results = []
            if results and results["documents"]:
                for i in range(len(results["documents"][0])):
                    distance = results["distances"][0][i]
                    # cosine distance -> similarity: 1 - distance
                    similarity = 1.0 - distance
                    search_results.append({
                        "text": results["documents"][0][i],
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "score": similarity,
                    })

            logger.info(f"向量检索完成: query长度={len(query)}, top_k={top_k}, 结果数={len(search_results)}")
            return search_results

        except Exception as e:
            raise VectorStoreError(
                "向量相似度检索失败",
                detail=str(e)
            )

    def delete_by_source(self, source_filename: str) -> int:
        """
        按文档来源删除对应的向量片段
        """
        try:
            # 先查询匹配的文档ID
            results = self._collection.get(
                where={"source": source_filename},
                include=["metadatas"],
            )

            if not results or not results["ids"]:
                logger.info(f"未找到文档 {source_filename} 的向量片段")
                return 0

            ids_to_delete = results["ids"]
            self._collection.delete(ids=ids_to_delete)

            logger.info(f"按来源删除向量: 文档={source_filename}, 删除数={len(ids_to_delete)}")
            return len(ids_to_delete)

        except Exception as e:
            raise VectorStoreError(
                f"按来源删除向量失败: {source_filename}",
                detail=str(e)
            )

    def delete_all(self) -> int:
        """
        清空整个向量库
        """
        try:
            count = self._collection.count()
            if count == 0:
                logger.info("向量库已为空，无需清空")
                return 0

            # 获取所有ID并删除
            all_data = self._collection.get(include=[])
            if all_data and all_data["ids"]:
                self._collection.delete(ids=all_data["ids"])

            logger.info(f"向量库已清空: 删除片段数={count}")
            return count

        except Exception as e:
            raise VectorStoreError(
                "清空向量库失败",
                detail=str(e)
            )

    def get_all_sources(self) -> List[str]:
        """
        获取向量库中所有文档来源名称（去重）
        """
        try:
            all_data = self._collection.get(include=["metadatas"])
            if not all_data or not all_data["metadatas"]:
                return []

            sources = set()
            for meta in all_data["metadatas"]:
                source = meta.get("source", "")
                if source:
                    sources.add(source)

            result = sorted(list(sources))
            logger.info(f"获取文档来源列表: 数量={len(result)}")
            return result

        except Exception as e:
            raise VectorStoreError(
                "获取文档来源列表失败",
                detail=str(e)
            )

    def count(self) -> int:
        """
        获取向量库中的文档片段总数
        """
        try:
            return self._collection.count()
        except Exception as e:
            raise VectorStoreError("获取向量库片段总数失败", detail=str(e))
