"""
金锤子 (GenForge) - 配置文件
"""
import os
from pathlib import Path


# 项目根目录
PROJECT_ROOT = Path(__file__).parent.parent

# ============ LLM 配置 ============
# 模式选择： "api" 或 "local"
LLM_MODE = "api"

# API 模式配置（API Key 从环境变量读取，永不硬编码！）
LLM_API_CONFIG = {
    "api_key": os.environ.get("DEEPSEEK_API_KEY", ""),
    "base_url": os.environ.get("DEEPSEEK_API_URL", "https://api.deepseek.com"),
    "model": os.environ.get("DEEPSEEK_MODEL", "deepseek-chat")
}

# 本地开源模型配置
LLM_LOCAL_CONFIG = {
    "model_path": "D:\\AI_Models\\qwen2.5-7b",
    "model_type": "qwen2.5",
    "quantization": "int4",
    "n_gpu_layers": 33,
    "context_length": 8192,
    "n_threads": 8,
}


def get_llm_config():
    """获取 LLM 配置"""
    if LLM_MODE == "api":
        return LLM_API_CONFIG
    else:
        return LLM_LOCAL_CONFIG


# ============ CAD 配置 ============
CAD_CONFIG = {
    "autocad_path": "C:\\Program Files\\Autodesk\\AutoCAD 2024",
    "autocad_dll_path": "C:\\Program Files\\Autodesk\\AutoCAD 2024",
}
