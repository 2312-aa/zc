"""
upload_kb_page.py — 知识库上传、文档管理页面
Streamlit前端页面，仅调用service层接口
"""
import streamlit as st

from core.vector_base.chroma_store import ChromaVectorStore
from service.knowledge_service import KnowledgeService
from utils.logger_util import get_logger
from config.settings import SUPPORTED_EXTENSIONS

logger = get_logger("UploadKBPage")


def _get_knowledge_service() -> KnowledgeService:
    """
    获取KnowledgeService实例（session_state缓存）
    Returns:
        KnowledgeService实例
    """
    if "knowledge_service" not in st.session_state:
        vector_store = _get_vector_store()
        st.session_state["knowledge_service"] = KnowledgeService(vector_store)
    return st.session_state["knowledge_service"]


def _get_vector_store() -> ChromaVectorStore:
    """
    获取ChromaVectorStore实例（session_state缓存）
    Returns:
        ChromaVectorStore实例
    """
    if "vector_store" not in st.session_state:
        st.session_state["vector_store"] = ChromaVectorStore()
    return st.session_state["vector_store"]


def render_upload_kb_page():
    """渲染知识库上传管理页面"""

    # 页面标题
    st.title("📚 知识库管理")
    st.markdown("---")

    # 初始化服务
    ks = _get_knowledge_service()

    # ============================================================
    # 侧边栏：知识库概览
    # ============================================================
    with st.sidebar:
        st.header("📊 知识库概览")
        doc_count = ks.get_document_count()
        doc_list = ks.get_all_documents()
        st.metric("向量片段总数", doc_count)
        st.metric("文档数量", len(doc_list))

        st.markdown("---")

        # 一键清空知识库
        st.header("⚠️ 危险操作")
        if st.button("🗑️ 清空知识库", type="secondary", use_container_width=True):
            st.session_state["confirm_clear"] = True

        if st.session_state.get("confirm_clear", False):
            st.warning("确认要清空所有知识库内容吗？此操作不可恢复！")
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ 确认清空", type="primary"):
                    result = ks.clear_all()
                    if result["success"]:
                        st.success(result["message"])
                    else:
                        st.error(result["message"])
                    st.session_state["confirm_clear"] = False
                    st.rerun()
            with col2:
                if st.button("❌ 取消"):
                    st.session_state["confirm_clear"] = False
                    st.rerun()

    # ============================================================
    # 主区域：文件上传
    # ============================================================
    st.header("📤 上传文档")
    supported_ext_str = ", ".join(sorted(SUPPORTED_EXTENSIONS))
    st.info(f"支持的文件格式: {supported_ext_str}")

    uploaded_files = st.file_uploader(
        "选择文件上传",
        type=[ext.lstrip(".") for ext in SUPPORTED_EXTENSIONS],
        accept_multiple_files=True,
        key="file_uploader",
    )

    if uploaded_files:
        for uploaded_file in uploaded_files:
            file_bytes = uploaded_file.read()
            filename = uploaded_file.name

            # 进度条容器
            progress_bar = st.progress(0.0, text=f"准备上传: {filename}")
            status_text = st.empty()

            def make_progress_callback(pb, st_text):
                """创建进度回调函数"""
                def callback(progress: float, message: str):
                    pb.progress(progress, text=message)
                    st_text.text(message)
                return callback

            progress_callback = make_progress_callback(progress_bar, status_text)

            # 执行上传
            result = ks.upload_file(
                file_bytes=file_bytes,
                filename=filename,
                progress_callback=progress_callback,
            )

            if result["success"]:
                progress_bar.progress(1.0, text="✅ " + result["message"])
                st.success(result["message"])
            else:
                progress_bar.empty()
                status_text.empty()
                st.error(result["message"])

    st.markdown("---")

    # ============================================================
    # 文档列表管理
    # ============================================================
    st.header("📋 已上传文档")

    doc_list = ks.get_all_documents()
    if not doc_list:
        st.info("知识库中暂无文档，请上传文件")
    else:
        st.write(f"共 {len(doc_list)} 个文档：")

        for doc_name in doc_list:
            with st.container():
                col1, col2 = st.columns([4, 1])
                with col1:
                    st.text(f"📄 {doc_name}")
                with col2:
                    if st.button("🗑️ 删除", key=f"del_{doc_name}"):
                        result = ks.delete_document(doc_name)
                        if result["success"]:
                            st.success(result["message"])
                        else:
                            st.error(result["message"])
                        st.rerun()
