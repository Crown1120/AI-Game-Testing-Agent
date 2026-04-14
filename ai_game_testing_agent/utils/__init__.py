"""
公共工具模块
包含超时处理、重试机制等共享功能
"""
import threading
import time
import random
from typing import Callable, Any, Tuple, Optional
from functools import wraps
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FuturesTimeoutError


class TimeoutException(Exception):
    """LLM 调用超时异常"""
    pass


class LLMInvocationError(Exception):
    """LLM 调用失败异常"""
    pass


def invoke_with_timeout(llm, messages, timeout: float = 30.0) -> Any:
    """带超时的 LLM 调用（线程安全版本）

    使用 ThreadPoolExecutor 替代手动线程管理，避免线程泄漏

    Args:
        llm: LLM 客户端实例
        messages: 消息列表
        timeout: 超时时间（秒）

    Returns:
        LLM 响应结果

    Raises:
        TimeoutException: 调用超时
        LLMInvocationError: 调用失败
    """
    def _invoke():
        return llm.invoke(messages)

    with ThreadPoolExecutor(max_workers=1) as executor:
        future = executor.submit(_invoke)
        try:
            return future.result(timeout=timeout)
        except FuturesTimeoutError:
            raise TimeoutException(f"LLM 调用超时（>{timeout}秒）")
        except Exception as e:
            raise LLMInvocationError(f"LLM 调用失败: {e}")


def retry_with_backoff(
    func: Optional[Callable] = None,
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff: float = 2.0,
    retry_exceptions: Tuple[type, ...] = (Exception,)
):
    """带指数退避的重试装饰器

    Args:
        func: 要装饰的函数
        max_retries: 最大重试次数
        base_delay: 初始延迟秒数
        max_delay: 最大延迟秒数
        backoff: 指数退避系数
        retry_exceptions: 需要重试的异常类型元组
    """
    if func is None:
        return lambda f: retry_with_backoff(
            f,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff=backoff,
            retry_exceptions=retry_exceptions
        )

    @wraps(func)
    def wrapper(*args, **kwargs):
        last_exception = None

        for attempt in range(max_retries):
            try:
                return func(*args, **kwargs)
            except retry_exceptions as e:
                last_exception = e
                if attempt < max_retries - 1:
                    # 计算延迟（带抖动，避免雷群效应）
                    delay = min(base_delay * (backoff ** attempt) + random.uniform(0, 0.1), max_delay)
                    print(f"⚠ {func.__name__} 失败 (尝试 {attempt + 1}/{max_retries}), {delay:.1f}s 后重试: {e}")
                    time.sleep(delay)

        # 所有重试都失败，抛出最后一个异常
        raise last_exception

    return wrapper


def invoke_with_retry(llm, messages, timeout: float = 30.0, max_retries: int = 3) -> Any:
    """带重试和超时的 LLM 调用

    Args:
        llm: LLM 客户端实例
        messages: 消息列表
        timeout: 单次调用超时时间（秒）
        max_retries: 最大重试次数

    Returns:
        LLM 响应结果
    """
    @retry_with_backoff(max_retries=max_retries, base_delay=1.0, retry_exceptions=(TimeoutException, LLMInvocationError))
    def _invoke():
        return invoke_with_timeout(llm, messages, timeout)

    return _invoke()


# 异步版本（可选）
async def async_retry_with_backoff(
    func: Optional[Callable] = None,
    *,
    max_retries: int = 3,
    base_delay: float = 1.0,
    max_delay: float = 10.0,
    backoff: float = 2.0,
    retry_exceptions: Tuple[type, ...] = (Exception,)
):
    """异步版本的重试装饰器"""
    import asyncio

    if func is None:
        return lambda f: async_retry_with_backoff(
            f,
            max_retries=max_retries,
            base_delay=base_delay,
            max_delay=max_delay,
            backoff=backoff,
            retry_exceptions=retry_exceptions
        )

    @wraps(func)
    async def wrapper(*args, **kwargs):
        last_exception = None

        for attempt in range(max_retries):
            try:
                return await func(*args, **kwargs)
            except retry_exceptions as e:
                last_exception = e
                if attempt < max_retries - 1:
                    delay = min(base_delay * (backoff ** attempt) + random.uniform(0, 0.1), max_delay)
                    print(f"⚠ {func.__name__} 失败 (尝试 {attempt + 1}/{max_retries}), {delay:.1f}s 后重试: {e}")
                    await asyncio.sleep(delay)

        raise last_exception

    return wrapper
