"""
ollama_check_util.py — 启动校验Ollama服务+两类模型是否就绪
检测11434端口Ollama服务是否运行，校验Embedding和LLM模型是否已拉取
Rerank复用Embedding模型，无需独立校验
"""
import requests
from utils.logger_util import get_logger
from config.llm_emb_config import (
    OLLAMA_BASE_URL,
    OLLAMA_EMBED_MODEL,
    OLLAMA_LLM_MODEL,
)
from utils.exception_util import ModelNotReadyError

logger = get_logger("OllamaCheck")


def check_ollama_service() -> bool:
    """
    检测Ollama服务是否在运行
    Returns:
        True: 服务正常; False: 服务不可用
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=5)
        if resp.status_code == 200:
            logger.info("Ollama服务连接正常")
            return True
        logger.warning(f"Ollama服务响应异常，状态码: {resp.status_code}")
        return False
    except requests.exceptions.ConnectionError:
        logger.error("无法连接Ollama服务，请确认服务已启动")
        return False
    except requests.exceptions.Timeout:
        logger.error("Ollama服务连接超时")
        return False
    except Exception as e:
        logger.error(f"Ollama服务检测异常: {str(e)}")
        return False


def get_local_models() -> list:
    """
    获取本地已拉取的模型列表
    Returns:
        模型名称列表
    """
    try:
        resp = requests.get(f"{OLLAMA_BASE_URL}/api/tags", timeout=10)
        if resp.status_code == 200:
            data = resp.json()
            models = [m.get("name", "") for m in data.get("models", [])]
            logger.info(f"本地已有模型: {models}")
            return models
        return []
    except Exception as e:
        logger.error(f"获取本地模型列表失败: {str(e)}")
        return []


def check_models_ready() -> dict:
    """
    校验三个必需模型是否已拉取就绪
    Returns:
        dict: {
            "ready": bool,          # 全部就绪
            "service_ok": bool,     # Ollama服务是否可用
            "missing": list,        # 缺失模型列表
            "pull_commands": list,  # 对应的拉取命令
        }
    """
    result = {
        "ready": False,
        "service_ok": False,
        "missing": [],
        "pull_commands": [],
    }

    # 检查Ollama服务
    if not check_ollama_service():
        result["service_ok"] = False
        return result

    result["service_ok"] = True

    # 获取本地已有模型
    local_models = get_local_models()
    # 规范化模型名（去除可能的tag后缀用于匹配）
    local_model_names = set()
    for m in local_models:
        local_model_names.add(m)
        # 兼容 "qwen:7b" 和 "qwen" 两种格式
        if ":" in m:
            local_model_names.add(m.split(":")[0])

    # 校验两个必需模型（Rerank复用Embedding模型，无需独立校验）
    required_models = {
        "embed": OLLAMA_EMBED_MODEL,
        "llm": OLLAMA_LLM_MODEL,
    }

    for model_type, model_name in required_models.items():
        if model_name not in local_model_names and model_name.split(":")[0] not in local_model_names:
            result["missing"].append(model_name)
            result["pull_commands"].append(f"ollama pull {model_name}")
            logger.warning(f"模型未就绪: {model_name} (类型: {model_type})")
        else:
            logger.info(f"模型已就绪: {model_name} (类型: {model_type})")

    result["ready"] = len(result["missing"]) == 0
    return result


def startup_check() -> None:
    """
    项目启动前置校验入口
    检测不通过则抛出ModelNotReadyError，附带修复命令提示
    """
    result = check_models_ready()

    if not result["service_ok"]:
        raise ModelNotReadyError(
            "Ollama服务未启动，请先运行Ollama服务",
            detail=f"请确认Ollama已安装并运行在 {OLLAMA_BASE_URL}"
        )

    if not result["ready"]:
        missing_str = "、".join(result["missing"])
        commands_str = "\n".join(result["pull_commands"])
        raise ModelNotReadyError(
            f"缺少必要模型: {missing_str}，请先拉取模型",
            detail=f"请执行以下命令拉取缺失模型:\n{commands_str}"
        )

    logger.info("Ollama服务及全部模型校验通过，系统就绪")
