from typing import TypedDict, List, Dict, Any, Optional
from typing_extensions import Annotated
import operator

class TestAgentState(TypedDict):
    """AI测试员的状态定义"""
    # 游戏核心状态
    game_state: Dict[str, Any]
    valid_actions: List[str]
    current_level: Optional[str]

    # AI推理信息
    observation: str
    reasoning: str
    next_action: Optional[str]

    # 测试管理
    steps_taken: int
    max_steps: int
    bugs_found: Annotated[List[Dict[str, Any]], operator.add]

    # 控制流
    is_finished: bool
    should_continue: bool
    error_message: Optional[str]

class DevAgentState(TypedDict):
    """AI测试开发员的状态定义"""
    # 输入
    test_report: Dict[str, Any]
    bug_list: List[Dict[str, Any]]

    # 分析结果
    failure_patterns: List[str]
    coverage_gaps: List[str]

    # 生成产物
    generated_code: str
    test_plan: Dict[str, Any]

    # 验证结果
    code_valid: bool
    execution_result: Optional[Dict[str, Any]]
