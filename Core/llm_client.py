"""
金锤子 (GenForge) - LLM 客户端
支持多轮对话历史、环境变量配置、代理

凭证从 .env 文件读取（勿提交 .env 到 git）
"""

import json
import logging
import os
import sys
import time
from pathlib import Path
from openai import OpenAI, APIError, AuthenticationError, RateLimitError

logger = logging.getLogger("GenForge.LLM")

# ── 配置读取（直接读取 .env 文件，不依赖 python-dotenv）─────────────
def _load_env():
    """从 .env 文件加载配置
    
    支持两种运行模式：
    1. 开发模式：从源代码目录读取 (publish/.env)
    2. 打包模式：从 EXE 所在目录读取 (dist/.env)
    """
    config = {}
    
    # 尝试路径列表（按优先级）
    possible_paths = []
    
    # 1. EXE 所在目录（打包后运行）
    # PyInstaller 打包后，sys.executable 指向 EXE 路径
    if hasattr(sys, '_MEIPASS'):
        # 打包模式：EXE 目录
        exe_dir = Path(sys.executable).parent
        possible_paths.append(exe_dir / ".env")
        # 也检查 MEIPASS 目录（资源文件所在）
        possible_paths.append(Path(sys._MEIPASS) / ".env")
    
    # 2. 源代码目录（开发模式）
    src_dir = Path(__file__).parent.parent
    possible_paths.append(src_dir / ".env")
    
    # 3. 当前工作目录
    possible_paths.append(Path.cwd() / ".env")
    
    # 按优先级尝试读取
    for env_path in possible_paths:
        if env_path.exists():
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            config[key.strip()] = value.strip()
                logger.info(f"✅ 已从 {env_path} 加载配置")
                return config
            except Exception as e:
                logger.warning(f"⚠️ 读取 {env_path} 失败: {e}")
    
    logger.warning("⚠️ 未找到 .env 文件")
    return config

_env_config = _load_env()

_API_KEY  = _env_config.get("DEEPSEEK_API_KEY") or os.getenv("DEEPSEEK_API_KEY") or os.getenv("API_KEY", "")
_API_URL  = _env_config.get("DEEPSEEK_API_URL") or os.getenv("DEEPSEEK_API_URL") or "https://api.deepseek.com/v1"
_MODEL    = _env_config.get("DEEPSEEK_MODEL") or os.getenv("DEEPSEEK_MODEL") or "deepseek-chat"
_PROXY_URL = _env_config.get("DEEPSEEK_PROXY_URL") or os.getenv("DEEPSEEK_PROXY_URL", "")

# 如果 .env 没有 key，尝试从 appsettings.json 读取（仅作回退，不推荐）
if not _API_KEY:
    _cfg_path = Path(__file__).parent.parent / "appsettings.json"
    try:
        with open(_cfg_path, "r", encoding="utf-8") as f:
            _settings = json.load(f)
        _API_KEY = _settings.get("AI_Chat", {}).get("ApiKey", "")
    except Exception:
        _API_KEY = ""

# 代理环境变量（OpenAI SDK 自动读取）
if _PROXY_URL:
    os.environ["HTTPS_PROXY"] = _PROXY_URL
    os.environ["HTTP_PROXY"]  = _PROXY_URL


class LLMClient:
    """LLM 客户端 - 支持多轮对话与角色切换"""

    def __init__(self):
        self.client = OpenAI(api_key=_API_KEY, base_url=_API_URL)
        self.model = _MODEL
        self.conversation_history: list = []
        logger.info(f"🤖 LLM 已初始化: {self.model} @ {_API_URL}")
        if _PROXY_URL:
            logger.info(f"🌐 代理已启用: {_PROXY_URL}")

    def chat(self, user_message: str, system_prompt: str = None,
             save_history: bool = True) -> str:
        """
        与 LLM 对话

        Args:
            user_message:  用户消息
            system_prompt: 角色系统提示（每次覆盖，不累积）
            save_history:  是否将此次对话写入历史
                          False → 内部推理专用（Architect/Developer 内部调用）
        """
        messages = []

        # 系统提示
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})

        # 历史对话（仅对外部对话生效）
        if save_history:
            messages.extend(self.conversation_history)

        messages.append({"role": "user", "content": user_message})

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
            )
            assistant_message = response.choices[0].message.content

            # 仅 save_history=True 时才写历史
            if save_history:
                self.conversation_history.append(
                    {"role": "user", "content": user_message}
                )
                self.conversation_history.append(
                    {"role": "assistant", "content": assistant_message}
                )
                # 历史超过 20 轮时自动压缩（参照 JZXZBOT Compaction 机制）
                if len(self.conversation_history) > 40:
                    self._compact_history()

            return assistant_message

        except Exception as e:
            logger.error(f"LLM 调用失败: {e}")
            raise RuntimeError(f"LLM 调用失败: {e}") from e

    def clear_history(self):
        """清空对话历史"""
        self.conversation_history = []

    def _compact_history(self):
        """
        简单压缩：保留最近 20 条消息（10轮对话）
        参照 JZXZBOT Compaction.PreserveRecentMessages = 10
        """
        keep = 20
        if len(self.conversation_history) > keep:
            self.conversation_history = self.conversation_history[-keep:]
            logger.info(f"♻️  对话历史已压缩，保留最近 {keep} 条")
