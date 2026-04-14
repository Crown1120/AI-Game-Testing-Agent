import os
import ast
from typing import Dict, Any, List
from langgraph.graph import StateGraph, END
from config import get_llm_client
from langchain_core.messages import HumanMessage, SystemMessage
from .state import DevAgentState
from utils import invoke_with_retry, TimeoutException, LLMInvocationError

# LLM 调用超时设置（秒）
LLM_TIMEOUT = 30

llm = get_llm_client()

def analyze_failures(state: DevAgentState) -> Dict[str, Any]:
    """分析Bug列表，提取失败模式"""
    bug_list = state.get('bug_list', [])
    if not bug_list:
        return {"failure_patterns": []}

    prompt = f"""分析以下游戏测试中发现的Bug列表，总结出3-5个常见的失败模式。
每个模式用一句话描述，以列表形式返回。

Bug列表:
{bug_list}
"""
    try:
        response = invoke_with_retry(llm, [HumanMessage(content=prompt)], timeout=LLM_TIMEOUT)
    except TimeoutException as e:
        print(f"⚠ {e}")
        return {"failure_patterns": []}
    except LLMInvocationError as e:
        print(f"⚠ {e}")
        return {"failure_patterns": []}

    patterns = [p.strip() for p in response.content.split('\n') if p.strip()]
    return {"failure_patterns": patterns}

def generate_test_code(state: DevAgentState) -> Dict[str, Any]:
    """根据失败模式生成 pytest 测试代码"""
    patterns = state.get('failure_patterns', [])

    prompt = f"""基于以下失败模式，生成 pytest 格式的自动化测试代码。
要求：
- 包含必要的 import 语句
- 每个失败模式对应至少一个测试函数
- 函数名以 test_ 开头
- 包含适当的断言
- 使用项目中的 SokobanEnv 类

失败模式:
{chr(10).join(patterns)}
"""
    try:
        response = invoke_with_retry(llm, [HumanMessage(content=prompt)], timeout=LLM_TIMEOUT)
    except TimeoutException as e:
        print(f"⚠ {e}")
        return {"generated_code": "# LLM timeout - no code generated"}
    except LLMInvocationError as e:
        print(f"⚠ {e}")
        return {"generated_code": "# LLM error - no code generated"}

    code = response.content
    # 提取代码块（如果被包裹在```python```中）
    if "```python" in code:
        code = code.split("```python")[1].split("```")[0]
    elif "```" in code:
        code = code.split("```")[1].split("```")[0]

    return {"generated_code": code.strip()}

def validate_code(state: DevAgentState) -> Dict[str, Any]:
    """验证生成的Python代码语法"""
    code = state.get('generated_code', '')
    try:
        ast.parse(code)
        valid = True
    except SyntaxError as e:
        valid = False
        state['execution_result'] = {"error": str(e)}

    return {"code_valid": valid}

def should_regenerate(state: DevAgentState) -> str:
    """判断是否需要重新生成"""
    if state.get('code_valid', False):
        return "save"
    # 简单起见，直接结束
    return "save"

def create_dev_agent():
    """创建AI测试开发员 LangGraph 图"""
    workflow = StateGraph(DevAgentState)

    workflow.add_node("analyze", analyze_failures)
    workflow.add_node("generate", generate_test_code)
    workflow.add_node("validate", validate_code)

    workflow.set_entry_point("analyze")
    workflow.add_edge("analyze", "generate")
    workflow.add_edge("generate", "validate")
    workflow.add_conditional_edges(
        "validate",
        should_regenerate,
        {
            "save": END,
            "regenerate": "generate"
        }
    )

    return workflow.compile()
