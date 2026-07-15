"""
base_vector.py — 向量存储抽象基类
定义向量库的增、删、查基础接口规范
"""
from abc import ABC, abstractmethod
from typing import List, Optional


class BaseVectorStore(ABC):
    """向量存储抽象基类，所有向量库实现必须继承此类"""

    @abstractmethod
    def add_texts(
        self,
        texts: List[str],
        metadatas: Optional[List[dict]] = None,
    ) -> List[str]:
        """
        批量添加文本到向量库
        Args:
            texts: 文本片段列表
            metadatas: 对应的元数据列表
        Returns:
            添加的文档ID列表
        """
        pass

    @abstractmethod
    def similarity_search(
        self,
        query: str,
        top_k: int = 6,
    ) -> List[dict]:
        """
        向量相似度检索
        Args:
            query: 查询文本
            top_k: 返回的最大结果数
        Returns:
            检索结果列表，格式: [{"text": str, "metadata": dict, "score": float}, ...]
        """
        pass

    @abstractmethod
    def delete_by_source(self, source_filename: str) -> int:
        """
        按文档来源删除对应的向量片段
        Args:
            source_filename: 文档文件名
        Returns:
            删除的片段数量
        """
        pass

    @abstractmethod
    def delete_all(self) -> int:
        """
        清空整个向量库
        Returns:
            删除的片段数量
        """
        pass

    @abstractmethod
    def get_all_sources(self) -> List[str]:
        """
        获取向量库中所有文档来源名称（去重）
        Returns:
            文档名称列表
        """
        pass

    @abstractmethod
    def count(self) -> int:
        """
        获取向量库中的文档片段总数
        Returns:
            片段总数
        """
        pass
