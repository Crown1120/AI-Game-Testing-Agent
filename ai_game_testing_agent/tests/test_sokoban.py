"""测试推箱子环境"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from game_env import SokobanEnv


def test_sokoban_reset():
    """测试重置游戏"""
    env = SokobanEnv(render_mode="text")
    state = env.reset()

    assert 'grid' in state
    assert 'player_pos' in state
    assert 'boxes' in state
    assert 'goals' in state


def test_sokoban_step():
    """测试执行动作"""
    env = SokobanEnv(render_mode="text")
    env.reset()

    # 获取初始状态
    initial_state = env.get_state_description()
    initial_steps = initial_state['steps']

    # 执行一个有效动作
    valid_actions = env.get_valid_actions()
    if valid_actions:
        action = valid_actions[0]
        new_state, reward, done, info = env.step(action)

        assert new_state['steps'] == initial_steps + 1
        assert isinstance(reward, float)
        assert isinstance(done, bool)


def test_sokoban_valid_actions():
    """测试获取合法动作"""
    env = SokobanEnv(render_mode="text")
    env.reset()

    valid_actions = env.get_valid_actions()
    assert isinstance(valid_actions, list)
    assert all(action in ['UP', 'DOWN', 'LEFT', 'RIGHT'] for action in valid_actions)


def test_sokoban_state_description():
    """测试状态描述"""
    env = SokobanEnv(render_mode="text")
    env.reset()

    state = env.get_state_description()

    assert 'grid' in state
    assert 'player_pos' in state
    assert 'boxes' in state
    assert 'goals' in state
    assert 'valid_actions' in state
    assert 'steps' in state
