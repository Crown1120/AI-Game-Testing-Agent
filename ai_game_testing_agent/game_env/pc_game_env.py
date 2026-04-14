"""
PC 桌面游戏环境适配器
支持通过图像识别和按键控制 PC 游戏
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import time
import subprocess
import os
import sys

# 设置输出编码
if sys.stdout.encoding != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from .base_env import GameEnvironment


class PCGameEnv(GameEnvironment):
    """
    PC 桌面游戏环境适配器

    支持通过图像识别（OpenCV）和按键控制（pyautogui）PC 游戏
    适用于没有 API 的独立游戏
    """

    def __init__(
        self,
        game_path: str = None,
        game_name: str = "Unknown Game",
        render_mode: str = "text",
        wait_for_start: int = 5
    ):
        """
        初始化 PC 游戏环境

        Args:
            game_path: 游戏可执行文件路径
            game_name: 游戏名称
            render_mode: 渲染模式
            wait_for_start: 启动等待时间（秒）
        """
        self.game_path = game_path
        self.game_name = game_name
        self.render_mode = render_mode
        self.wait_for_start = wait_for_start
        self.process = None
        self.is_connected = False

        self._start_game()

    def _start_game(self):
        """启动游戏进程"""
        if not self.game_path:
            print("⚠ 未指定游戏路径，使用模拟模式")
            return

        try:
            if os.path.exists(self.game_path):
                self.process = subprocess.Popen([self.game_path])
                # 使用英文消息避免编码问题
                print(f"[OK] Game started: {self.game_name}")
                print(f"  Waiting {self.wait_for_start} seconds...")
                time.sleep(self.wait_for_start)
                self.is_connected = True
            else:
                print(f"[WARN] Game path not found: {self.game_path}")
        except Exception as e:
            print(f"[ERROR] Failed to start game: {e}")

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            # 重启游戏
            if self.process:
                self.process.terminate()
                time.sleep(1)
                self.process = subprocess.Popen([self.game_path])
                time.sleep(self.wait_for_start)

            return self.get_state_description()
        except Exception as e:
            print(f"[ERROR] Reset failed: {e}")
            return self._get_fallback_state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        if not self.is_connected:
            return self._get_fallback_state(), 0.0, True, {"error": "Not connected"}

        try:
            self._execute_action(action)
            time.sleep(0.1)  # 等待游戏响应

            new_state = self.get_state_description()
            return new_state, 0.0, False, {}
        except Exception as e:
            print(f"[ERROR] Action failed: {e}")
            return self._get_fallback_state(), 0.0, True, {"error": str(e)}

    def get_valid_actions(self) -> List[str]:
        """获取合法动作"""
        # 通过图像识别检测可交互元素
        return [
            'MOVE_UP', 'MOVE_DOWN', 'MOVE_LEFT', 'MOVE_RIGHT',
            'JUMP', 'CROUCH', 'RUN',
            'ATTACK', 'USE', 'INTERACT',
            'OPEN_MENU', 'PAUSE'
        ]

    def render(self) -> np.ndarray:
        """获取游戏画面"""
        import pyautogui

        if not self.is_connected:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

        try:
            # 截取屏幕
            screenshot = pyautogui.screenshot()
            return np.array(screenshot)
        except Exception as e:
            print(f"[ERROR] Screenshot failed: {e}")
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            import pyautogui

            # 获取屏幕尺寸
            screen_size = pyautogui.size()

            state = {
                "screen_size": list(screen_size),
                "screenshot_available": True,
                "type": "pc_game",
                "game_name": self.game_name
            }

            return state
        except Exception as e:
            return self._get_fallback_state()

    def _execute_action(self, action: str):
        """执行具体动作"""
        import pyautogui

        # 键盘映射
        key_map = {
            'MOVE_UP': 'w',
            'MOVE_DOWN': 's',
            'MOVE_LEFT': 'a',
            'MOVE_RIGHT': 'd',
            'JUMP': 'space',
            'CROUCH': 'ctrl',
            'RUN': 'shift',
            'ATTACK': 'left_click',
            'USE': 'e',
            'INTERACT': 'f',
            'OPEN_MENU': 'esc',
            'PAUSE': 'p'
        }

        key = key_map.get(action, None)
        if key:
            if 'click' in key:
                pyautogui.click()
            else:
                pyautogui.press(key)

    def _get_fallback_state(self) -> Dict[str, Any]:
        return {
            "grid": "Game not running",
            "valid_actions": ["MOVE_UP", "MOVE_DOWN", "MOVE_LEFT", "MOVE_RIGHT"],
            "steps": 0
        }

    def is_solvable(self) -> bool:
        return True

    def close(self):
        """关闭游戏"""
        if self.process:
            self.process.terminate()


class StandaloneGameEnv(PCGameEnv):
    """
    独立游戏专用适配器
    """
    pass


class RetroGameEnv(PCGameEnv):
    """
    复古游戏（模拟器）专用适配器
    """

    def __init__(self, game_path: str = None, emulator_path: str = None, **kwargs):
        super().__init__(game_path, **kwargs)
        self.emulator_path = emulator_path

    def _execute_action(self, action: str):
        """执行复古游戏特定动作"""
        import pyautogui

        # 任天堂风格按键映射
        retro_map = {
            'MOVE_UP': 'up',
            'MOVE_DOWN': 'down',
            'MOVE_LEFT': 'left',
            'MOVE_RIGHT': 'right',
            'JUMP': 'z',
            'ATTACK': 'x',
            'SELECT': 'enter',
            'START': 'space'
        }

        key = retro_map.get(action, None)
        if key:
            pyautogui.press(key)
