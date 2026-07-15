"""
file_util.py — 通用文件工具集
提供MD5文件去重、目录创建、文件格式校验等功能
"""
import hashlib
import os
from pathlib import Path
from utils.logger_util import get_logger
from config.settings import SUPPORTED_EXTENSIONS, UPLOAD_FILE_PATH

logger = get_logger("FileUtil")


def compute_file_md5(file_path: str) -> str:
    """
    计算文件的MD5哈希值，用于文件去重
    Args:
        file_path: 文件绝对路径
    Returns:
        MD5十六进制字符串
    """
    md5_hash = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            md5_hash.update(chunk)
    return md5_hash.hexdigest()


def compute_bytes_md5(file_bytes: bytes) -> str:
    """
    计算字节数据的MD5哈希值
    Args:
        file_bytes: 文件字节数据
    Returns:
        MD5十六进制字符串
    """
    return hashlib.md5(file_bytes).hexdigest()


def ensure_dir(dir_path: str) -> None:
    """
    确保目录存在，不存在则递归创建
    Args:
        dir_path: 目录路径
    """
    Path(dir_path).mkdir(parents=True, exist_ok=True)


def validate_file_extension(filename: str) -> bool:
    """
    校验文件扩展名是否在支持列表中
    Args:
        filename: 文件名
    Returns:
        True/False
    """
    ext = Path(filename).suffix.lower()
    if ext not in SUPPORTED_EXTENSIONS:
        logger.warning(f"不支持的文件格式: {ext}，文件名: {filename}")
        return False
    return True


def save_upload_file(file_bytes: bytes, filename: str) -> str:
    """
    保存上传文件到指定目录
    Args:
        file_bytes: 文件字节数据
        filename: 原始文件名
    Returns:
        保存后的文件绝对路径
    """
    ensure_dir(UPLOAD_FILE_PATH)
    save_path = os.path.join(UPLOAD_FILE_PATH, filename)
    with open(save_path, "wb") as f:
        f.write(file_bytes)
    logger.info(f"文件已保存: {save_path}")
    return save_path


def get_all_uploaded_files() -> list:
    """
    获取所有已上传的文件列表
    Returns:
        文件名列表
    """
    upload_dir = Path(UPLOAD_FILE_PATH)
    if not upload_dir.exists():
        return []
    return [f.name for f in upload_dir.iterdir() if f.is_file()]


def delete_uploaded_file(filename: str) -> bool:
    """
    删除指定上传文件
    Args:
        filename: 文件名
    Returns:
        是否删除成功
    """
    file_path = os.path.join(UPLOAD_FILE_PATH, filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        logger.info(f"已删除上传文件: {file_path}")
        return True
    logger.warning(f"文件不存在，无法删除: {file_path}")
    return False
