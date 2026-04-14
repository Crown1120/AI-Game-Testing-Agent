#!/usr/bin/env python3
"""
命令行交互界面，用于手动调试
"""
import cmd
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from game_env import SokobanEnv
from agent import create_test_agent

class GameTestCLI(cmd.Cmd):
    intro = "欢迎使用AI游戏测试系统 CLI。输入 help 查看命令。"
    prompt = "(ai-test) "

    def __init__(self):
        super().__init__()
        self.env = SokobanEnv(render_mode="human")
        self.env.reset()
        self.agent = None

    def do_show(self, arg):
        """显示当前游戏状态"""
        state = self.env.get_state_description()
        print(state['grid'])
        print(f"可行动作: {state['valid_actions']}")
        print(f"步数: {state['steps']}")

    def do_move(self, arg):
        """执行移动: move UP/DOWN/LEFT/RIGHT"""
        arg = arg.strip().upper()
        if arg in ['UP', 'DOWN', 'LEFT', 'RIGHT']:
            state, reward, done, info = self.env.step(arg)
            self.do_show("")
            if done:
                print("游戏结束！")
        else:
            print("无效动作，请使用 UP/DOWN/LEFT/RIGHT")

    def do_reset(self, arg):
        """重置游戏"""
        self.env.reset()
        self.do_show("")

    def do_run_agent(self, arg):
        """运行AI测试员"""
        steps = int(arg) if arg.isdigit() else 20
        self.agent = create_test_agent(self.env)
        initial = {
            "game_state": self.env.get_state_description(),
            "valid_actions": self.env.get_valid_actions(),
            "steps_taken": 0,
            "max_steps": steps,
            "bugs_found": [],
            "should_continue": True,
            "is_finished": False,
        }
        print(f"运行AI测试员，最大步数: {steps}")
        result = self.agent.invoke(initial)
        print(f"完成。步数: {result['steps_taken']}, 发现Bug: {len(result['bugs_found'])}")

    def do_exit(self, arg):
        """退出"""
        print("再见！")
        return True

    def do_quit(self, arg):
        return self.do_exit(arg)

if __name__ == "__main__":
    GameTestCLI().cmdloop()
