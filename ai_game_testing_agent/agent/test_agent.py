import os
from typing import Dict, Any
from langgraph.graph import StateGraph, END
from config import get_llm_client
from langchain_core.messages import HumanMessage, SystemMessage
from .state import TestAgentState
from utils import invoke_with_retry, TimeoutException, LLMInvocationError

# LLM 调用超时设置（秒）
LLM_TIMEOUT = 30

llm = get_llm_client()

def observe_and_reason(state: TestAgentState) -> Dict[str, Any]:
    """观察游戏状态并推理下一步"""
    game_state = state['game_state']
    valid_actions = state.get('valid_actions', [])

    system_prompt = """你是一个专业的游戏测试员。你的任务是：
    1. 分析当前游戏状态
    2. 规划下一步行动策略
    3. 识别潜在的Bug或异常情况

    请以JSON格式输出，包含 reasoning 和 observation 字段。"""

    try:
        response = invoke_with_retry(
            llm, [
                SystemMessage(content=system_prompt),
                HumanMessage(content=f"当前状态: {game_state}\n可行动作: {valid_actions}")
            ],
            timeout=LLM_TIMEOUT
        )
    except TimeoutException as e:
        print(f"⚠ {e}")
        return {"observation": "LLM timeout", "reasoning": "LLM timeout"}
    except LLMInvocationError as e:
        print(f"⚠ {e}")
        return {"observation": "LLM error", "reasoning": "LLM error"}

    # 简化处理：直接使用响应内容
    content = response.content
    return {
        "observation": content,
        "reasoning": content
    }

def decide_action(state: TestAgentState) -> Dict[str, Any]:
    """从可行动作中选择一个"""
    reasoning = state.get('reasoning', '')
    valid_actions = state.get('valid_actions', [])

    if not valid_actions:
        return {"next_action": None, "should_continue": False}

    prompt = f"""基于以下推理，选择下一步动作。只输出动作名称（UP/DOWN/LEFT/RIGHT之一）。

推理内容: {reasoning}
可选项: {valid_actions}
"""
    try:
        response = invoke_with_retry(
            llm, [HumanMessage(content=prompt)],
            timeout=LLM_TIMEOUT
        )
        chosen = response.content.strip().upper()
        if chosen not in valid_actions:
            chosen = valid_actions[0]
    except (TimeoutException, LLMInvocationError) as e:
        print(f"⚠ 动作选择失败: {e}")
        chosen = valid_actions[0] if valid_actions else None

    return {"next_action": chosen}

def execute_action(state: TestAgentState, env) -> Dict[str, Any]:
    """执行动作并更新状态（此节点需要外部环境注入）"""
    # 注意：实际执行需要将 env 通过 partial 或闭包传入
    # 这里仅返回占位，实际运行时在 create_test_agent 中绑定
    return {}

def validate_state(state: TestAgentState) -> Dict[str, Any]:
    """验证游戏状态是否异常"""
    game_state = state['game_state']
    bugs = []

    # 检查玩家位置合法性
    if game_state.get('player_pos') is None:
        bugs.append({
            "type": "player_out_of_bounds",
            "severity": "high",
            "description": "玩家位置丢失",
            "step": state['steps_taken']
        })

    # 检查箱子数量是否与目标点匹配
    if game_state.get('total_goals', 0) != len(game_state.get('boxes', [])):
        bugs.append({
            "type": "box_goal_mismatch",
            "severity": "medium",
            "description": "箱子数量与目标点数量不匹配",
            "step": state['steps_taken']
        })

    return {"bugs_found": bugs}

def should_continue(state: TestAgentState) -> str:
    """判断是否继续执行"""
    if state.get('is_finished', False):
        return "end"
    if state.get('steps_taken', 0) >= state.get('max_steps', 100):
        return "end"
    if not state.get('should_continue', True):
        return "end"
    return "continue"

def create_test_agent(env):
    """创建AI测试员 LangGraph 图，绑定游戏环境"""

    def execute_action_bound(state: TestAgentState) -> Dict[str, Any]:
        """绑定了环境的动作执行节点"""
        action = state.get('next_action')
        if not action:
            return {"should_continue": False}

        new_state, reward, done, info = env.step(action)
        steps = state.get('steps_taken', 0) + 1

        return {
            "game_state": new_state,
            "valid_actions": env.get_valid_actions(),
            "steps_taken": steps,
            "is_finished": done,
            "should_continue": not done
        }

    workflow = StateGraph(TestAgentState)

    # 添加节点
    workflow.add_node("observe", observe_and_reason)
    workflow.add_node("decide", decide_action)
    workflow.add_node("execute", execute_action_bound)
    workflow.add_node("validate", validate_state)

    # 添加边
    workflow.set_entry_point("observe")
    workflow.add_edge("observe", "decide")
    workflow.add_edge("decide", "execute")
    workflow.add_edge("execute", "validate")
    workflow.add_conditional_edges(
        "validate",
        should_continue,
        {
            "continue": "observe",
            "end": END
        }
    )

    return workflow.compile()
