#!/usr/bin/env python3
"""
AI游戏测试系统主入口
支持多种游戏平台：Unity、Web、微信小游戏、PC 游戏等
"""
import os
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

# 添加项目根目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

load_dotenv()

from game_env import (
    SokobanEnv,
    Unity3DEnv,
    Unity2DEnv,
    WebGameEnv,
    WeChatMiniGameEnv,
    PCGameEnv
)
from agent import create_test_agent, create_dev_agent
from agent.state import TestAgentState, DevAgentState
from config import config

# 游戏环境注册表
GAME_ENVIRONMENTS = {
    "sokoban": SokobanEnv,
    "unity3d": Unity3DEnv,
    "unity2d": Unity2DEnv,
    "web": WebGameEnv,
    "wechat": WeChatMiniGameEnv,
    "pc": PCGameEnv,
}


def get_game_env(env_name: str, **kwargs):
    """获取游戏环境实例"""
    env_class = GAME_ENVIRONMENTS.get(env_name)
    if not env_class:
        raise ValueError(f"不支持的游戏环境: {env_name}")
    return env_class(**kwargs)


def run_test_session(
    env_name: str = "sokoban",
    level_id: str = "default",
    max_steps: int = 50,
    **kwargs
):
    """运行一次完整的测试会话"""
    print(f"🚀 启动AI游戏测试会话")
    print(f"  游戏平台: {env_name}")
    print(f"  关卡: {level_id}")

    # 初始化游戏环境
    env_class = GAME_ENVIRONMENTS.get(env_name)
    if not env_class:
        raise ValueError(f"不支持的游戏环境: {env_name}")

    env = env_class(**kwargs)
    env.reset(level_id)

    # 创建测试员智能体
    test_agent = create_test_agent(env)

    # 初始状态
    initial_state: TestAgentState = {
        "game_state": env.get_state_description(),
        "valid_actions": env.get_valid_actions(),
        "current_level": level_id,
        "observation": "",
        "reasoning": "",
        "next_action": None,
        "steps_taken": 0,
        "max_steps": max_steps,
        "bugs_found": [],
        "is_finished": False,
        "should_continue": True,
        "error_message": None
    }

    print("🎮 AI测试员开始探索...")
    final_state = test_agent.invoke(initial_state)

    print(f"✅ 探索完成，共执行 {final_state['steps_taken']} 步")
    print(f"🐞 发现 {len(final_state['bugs_found'])} 个潜在Bug")

    # 生成测试报告
    report = {
        "session_id": datetime.now().strftime("%Y%m%d_%H%M%S"),
        "env_type": env_name,
        "level": level_id,
        "steps_taken": final_state['steps_taken'],
        "bugs": final_state['bugs_found'],
        "final_game_state": final_state['game_state']
    }

    os.makedirs("data/reports", exist_ok=True)
    report_path = f"data/reports/report_{report['session_id']}.json"
    try:
        with open(report_path, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"📄 测试报告已保存: {report_path}")
    except IOError as e:
        print(f"⚠ 保存报告失败: {e}")

    # 启动测试开发员
    if final_state['bugs_found']:
        print("\n🛠️ AI测试开发员开始分析并生成回归测试...")
        dev_agent = create_dev_agent()

        dev_state: DevAgentState = {
            "test_report": report,
            "bug_list": final_state['bugs_found'],
            "failure_patterns": [],
            "coverage_gaps": [],
            "generated_code": "",
            "test_plan": {},
            "code_valid": False,
            "execution_result": None
        }

        dev_result = dev_agent.invoke(dev_state)

        # 保存生成的测试代码
        os.makedirs("tests/generated_tests", exist_ok=True)
        code_path = f"tests/generated_tests/test_autogen_{report['session_id']}.py"
        try:
            with open(code_path, 'w') as f:
                f.write(dev_result.get('generated_code', '# No code generated'))
            print(f"📝 已生成测试代码: {code_path}")
        except IOError as e:
            print(f"⚠ 保存测试代码失败: {e}")
        print(f"🔍 代码语法验证: {'通过' if dev_result.get('code_valid') else '失败'}")
    else:
        print("✨ 未发现Bug，跳过测试代码生成。")

    print("\n🎉 测试会话完成！")
    return report


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description="AI游戏测试系统")
    parser.add_argument(
        "--env",
        type=str,
        default="sokoban",
        choices=list(GAME_ENVIRONMENTS.keys()),
        help="游戏平台类型"
    )
    parser.add_argument("--level", type=str, default="default", help="关卡ID")
    parser.add_argument("--steps", type=int, default=50, help="最大测试步数")
    parser.add_argument("--api-url", type=str, help="API 服务器地址（适用于 Unity/Web）")
    parser.add_argument("--game-path", type=str, help="游戏可执行文件路径（适用于 PC 游戏）")
    args = parser.parse_args()

    # 构建额外参数
    kwargs = {}
    if args.api_url:
        kwargs["api_url"] = args.api_url
    if args.game_path:
        kwargs["game_path"] = args.game_path

    run_test_session(args.env, args.level, args.steps, **kwargs)


if __name__ == "__main__":
    main()
