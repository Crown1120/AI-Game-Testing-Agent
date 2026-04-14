"""测试配置模块"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import Config, is_xf_yun_api, get_llm_client


def test_config_defaults():
    """测试配置默认值"""
    assert Config.OPENAI_API_KEY is not None
    assert Config.OPENAI_BASE_URL is not None
    assert Config.LLM_MODEL is not None
    assert Config.MAX_TEST_STEPS == 100
    assert Config.TEMPERATURE == 0.1


def test_is_xf_yun_api():
    """测试讯飞API检测"""
    # 重置模块以重新加载配置
    import importlib
    import config

    # 讯飞API
    os.environ['OPENAI_BASE_URL'] = 'https://api.xf-yun.com/v1'
    importlib.reload(config)
    assert config.is_xf_yun_api() is True

    # 非讯飞API
    os.environ['OPENAI_BASE_URL'] = 'https://api.openai.com/v1'
    importlib.reload(config)
    assert config.is_xf_yun_api() is False


def test_get_llm_client():
    """测试LLM客户端创建"""
    client = get_llm_client()
    assert client is not None
