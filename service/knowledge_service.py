"""
knowledge_service.py — 知识库业务服务层
文件上传、切片入库、文档删除、知识库管理
UI层仅调用该层接口，不包含切片、向量、重排底层逻辑
"""
import threading
from typing import List, Optional, Callable

from core.file_parser import parse_file
from core.text_splitter import split_text_with_metadata
from core.vector_base.chroma_store import ChromaVectorStore
from utils.logger_util import get_logger
from utils.exception_util import (
    FileValidationError,
    VectorStoreError,
    FileParseError,
    handle_exception,
)
from utils.file_util import (
    compute_bytes_md5,
    save_upload_file,
    validate_file_extension,
    delete_uploaded_file,
    ensure_dir,
)
from config.settings import UPLOAD_FILE_PATH, CHUNK_SIZE, CHUNK_OVERLAP

logger = get_logger("KnowledgeService")

# 已上传文件的MD5缓存，用于去重
_uploaded_md5_set: set = set()


def _load_existing_md5_set(vector_store: ChromaVectorStore) -> set:
    """
    从向量库元数据中加载已有文件的MD5集合
    Args:
        vector_store: 向量库实例
    Returns:
        MD5集合
    """
    # 通过向量库中的source字段获取已有文档名
    sources = vector_store.get_all_sources()
    return set(sources)


class KnowledgeService:
    """知识库业务服务"""

    def __init__(self, vector_store: ChromaVectorStore):
        self._vector_store = vector_store
        # 初始化时加载已有MD5集合
        global _uploaded_md5_set
        _uploaded_md5_set = _load_existing_md5_set(vector_store)

    def upload_file(
        self,
        file_bytes: bytes,
        filename: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> dict:
        """
        上传文件到知识库
        Args:
            file_bytes: 文件字节数据
            filename: 文件名
            progress_callback: 进度回调函数 (progress: float, message: str)
        Returns:
            {"success": bool, "message": str, "chunks": int}
        """
        try:
            # 1. 校验文件格式
            if not validate_file_extension(filename):
                raise FileValidationError(
                    f"不支持的文件格式: {filename}",
                    detail=f"支持格式: pdf/txt/md/docx/xlsx"
                )

            # 2. MD5去重校验
            file_md5 = compute_bytes_md5(file_bytes)
            if file_md5 in _uploaded_md5_set:
                logger.info(f"文件已存在，跳过上传: {filename} (MD5: {file_md5})")
                return {
                    "success": True,
                    "message": f"文件 '{filename}' 已存在，跳过重复上传",
                    "chunks": 0,
                }

            if progress_callback:
                progress_callback(0.1, "文件校验通过，开始保存...")

            # 3. 保存原始文件
            save_path = save_upload_file(file_bytes, filename)

            if progress_callback:
                progress_callback(0.2, "文件保存成功，开始解析...")

            # 4. 解析文件
            text = parse_file(save_path)

            if not text.strip():
                return {
                    "success": False,
                    "message": f"文件 '{filename}' 解析后内容为空",
                    "chunks": 0,
                }

            if progress_callback:
                progress_callback(0.4, "文件解析完成，开始切片...")

            # 5. 文本切片
            chunks = split_text_with_metadata(
                text=text,
                source_filename=filename,
                chunk_size=CHUNK_SIZE,
                chunk_overlap=CHUNK_OVERLAP,
            )

            if not chunks:
                return {
                    "success": False,
                    "message": f"文件 '{filename}' 切片后无有效内容",
                    "chunks": 0,
                }

            if progress_callback:
                progress_callback(0.6, f"切片完成，共{len(chunks)}个片段，开始向量化入库...")

            # 6. 批量向量化入库
            texts = [c["text"] for c in chunks]
            metadatas = [c["metadata"] for c in chunks]
            # 添加MD5到元数据
            for meta in metadatas:
                meta["file_md5"] = file_md5

            self._vector_store.add_texts(texts=texts, metadatas=metadatas)

            # 7. 记录MD5
            _uploaded_md5_set.add(file_md5)

            if progress_callback:
                progress_callback(1.0, f"入库完成！共{len(chunks)}个向量片段")

            logger.info(f"文件上传入库成功: {filename}, 片段数={len(chunks)}")
            return {
                "success": True,
                "message": f"文件 '{filename}' 上传成功，共生成 {len(chunks)} 个知识片段",
                "chunks": len(chunks),
            }

        except Exception as e:
            error_msg = handle_exception(e)
            logger.error(f"文件上传失败: {filename}, 原因: {error_msg}")
            return {
                "success": False,
                "message": f"上传失败: {error_msg}",
                "chunks": 0,
            }

    def upload_file_async(
        self,
        file_bytes: bytes,
        filename: str,
        progress_callback: Optional[Callable[[float, str], None]] = None,
    ) -> threading.Thread:
        """
        异步上传文件（后台线程执行，页面不阻塞）
        Args:
            file_bytes: 文件字节数据
            filename: 文件名
            progress_callback: 进度回调函数
        Returns:
            后台线程对象
        """
        thread = threading.Thread(
            target=self.upload_file,
            args=(file_bytes, filename, progress_callback),
            daemon=True,
        )
        thread.start()
        return thread

    def delete_document(self, filename: str) -> dict:
        """
        按文档名删除对应的向量片段
        Args:
            filename: 文档文件名
        Returns:
            {"success": bool, "message": str, "deleted_count": int}
        """
        try:
            deleted_count = self._vector_store.delete_by_source(filename)
            # 同时删除原始上传文件
            delete_uploaded_file(filename)
            # 从MD5集合中移除
            _uploaded_md5_set.discard(filename)

            logger.info(f"文档删除完成: {filename}, 删除片段数={deleted_count}")
            return {
                "success": True,
                "message": f"文档 '{filename}' 已删除，共清除 {deleted_count} 个向量片段",
                "deleted_count": deleted_count,
            }
        except Exception as e:
            error_msg = handle_exception(e)
            return {
                "success": False,
                "message": f"删除失败: {error_msg}",
                "deleted_count": 0,
            }

    def clear_all(self) -> dict:
        """
        一键清空整个向量库
        Returns:
            {"success": bool, "message": str, "deleted_count": int}
        """
        try:
            deleted_count = self._vector_store.delete_all()
            # 清空MD5缓存
            _uploaded_md5_set.clear()

            logger.info(f"向量库已清空: 删除片段数={deleted_count}")
            return {
                "success": True,
                "message": f"知识库已清空，共清除 {deleted_count} 个向量片段",
                "deleted_count": deleted_count,
            }
        except Exception as e:
            error_msg = handle_exception(e)
            return {
                "success": False,
                "message": f"清空失败: {error_msg}",
                "deleted_count": 0,
            }

    def get_all_documents(self) -> List[str]:
        """
        获取知识库中所有已上传文档名称
        Returns:
            文档名称列表
        """
        return self._vector_store.get_all_sources()

    def get_document_count(self) -> int:
        """
        获取知识库中的文档片段总数
        Returns:
            片段总数
        """
        return self._vector_store.count()
