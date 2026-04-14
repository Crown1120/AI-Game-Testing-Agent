import os
import random
from typing import Optional, Callable, Any, Tuple
from functools import wraps

from dotenv import load_dotenv

load_dotenv()

class Config:
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    LLM_MODEL = os.getenv("LLM_MODEL", "gpt-4o")
    MAX_TEST_STEPS = 100
    TEMPERATURE = 0.1
    CHECKPOINT_DB_PATH = "data/checkpoints.db"

    # 重试配置
    MAX_RETRIES = 3
    RETRY_BASE_DELAY = 1.0  # 秒
    RETRY_MAX_DELAY = 10.0  # 秒
    RETRY_BACKOFF = 2.0  # 指数退避系数
    TIMEOUT = 30  # LLM 超时秒数


# 检测是否为讯飞 API
def is_xf_yun_api() -> bool:
    """检测是否使用讯飞 API"""
    base_url = Config.OPENAI_BASE_URL
    return "xf-yun.com" in base_url


def get_llm_client():
    """获取配置好的 LLM 客户端"""
    from langchain_openai import ChatOpenAI

    base_url = Config.OPENAI_BASE_URL
    # 讯飞 API 的 base_url 需要指向 /v1 路径
    if base_url.endswith("/anthropic"):
        base_url = base_url.replace("/anthropic", "")
    if not base_url.endswith("/v1"):
        base_url = base_url.rstrip("/") + "/v1"

    # 安全日志：不打印敏感信息
    print(f"使用 API 端点: {base_url}")
    print(f"使用模型: {Config.LLM_MODEL}")
    # API Key 状态检查（不打印实际值）
    if not Config.OPENAI_API_KEY:
        raise ValueError("OPENAI_API_KEY 未设置，请检查环境变量或 .env 文件")
    if len(Config.OPENAI_API_KEY) < 10:
        print("⚠ 警告: API Key 长度异常，请检查配置")

    return ChatOpenAI(
        model=Config.LLM_MODEL,
        temperature=Config.TEMPERATURE,
        api_key=Config.OPENAI_API_KEY,
        base_url=base_url
    )


config = Config()
