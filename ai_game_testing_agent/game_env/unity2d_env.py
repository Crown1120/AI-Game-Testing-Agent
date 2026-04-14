"""
Unity 2D 游戏环境适配器
适用于 Unity 2D 游戏测试
"""
import requests
import json
import time
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import base64
from io import BytesIO

from .base_env import GameEnvironment


class Unity2DEnv(GameEnvironment):
    """
    Unity 2D 游戏环境适配器

    支持通过 HTTP API 连接 Unity 2D 游戏
    适用于平台游戏、解谜游戏等 2D 场景
    """

    # 默认动作空间
    ACTION_SPACE = [
        'UP', 'DOWN', 'LEFT', 'RIGHT',      # 移动
        'JUMP', 'CROUCH', 'RUN',            # 动作
        'ATTACK', 'USE_ITEM', 'INTERACT',   # 交互
        'NONE'                              # 无动作
    ]

    def __init__(
        self,
        api_url: str = "http://localhost:8081",
        api_key: str = None,
        render_mode: str = "text",
        timeout: int = 10,
        max_steps: int = 500
    ):
        """
        初始化 Unity 2D 环境

        Args:
            api_url: Unity API 服务器地址
            api_key: API 认证密钥
            render_mode: 渲染模式 ('text' 或 'human')
            timeout: 请求超时时间
            max_steps: 最大步数
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.render_mode = render_mode
        self.timeout = timeout
        self.max_steps = max_steps
        self.steps = 0
        self.is_connected = False
        self.current_state = None

        self._connect()

    def _connect(self):
        """连接到 Unity API 服务器"""
        try:
            response = requests.get(
                f"{self.api_url}/status",
                headers=self._get_headers(),
                timeout=self.timeout
            )
            if response.status_code == 200:
                info = response.json()
                self.is_connected = True
                self.ACTION_SPACE = info.get("actions", self.ACTION_SPACE)
                print(f"✓ 已连接到 Unity 2D 游戏")
                print(f"  动作空间: {self.ACTION_SPACE}")
        except Exception as e:
            print(f"⚠ 连接失败: {e}")

    def _get_headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _api_post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        try:
            response = requests.post(
                f"{self.api_url}{endpoint}",
                json=data,
                headers=self._get_headers(),
                timeout=self.timeout
            )
            if response.status_code == 200:
                return response.json()
        except Exception as e:
            print(f"API 错误: {e}")
        return None

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏"""
        self.steps = 0
        data = {"level_id": level_id} if level_id else {}
        response = self._api_post("/reset", data)

        if response:
            self.current_state = response
            return self.get_state_description()
        return self._get_fallback_state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        self.steps += 1

        if not self.is_connected:
            return self._get_fallback_state(), 0.0, True, {"error": "Not connected"}

        response = self._api_post("/step", {"action": action})

        if response:
            new_state = response.get("state", {})
            reward = response.get("reward", 0.0)
            done = response.get("done", False)
            info = response.get("info", {})

            # 检查是否超时
            if self.steps >= self.max_steps:
                done = True

            self.current_state = new_state
            return new_state, reward, done, info

        return self._get_fallback_state(), 0.0, True, {"error": "API failed"}

    def get_valid_actions(self) -> List[str]:
        """获取合法动作"""
        if not self.is_connected:
            return self.ACTION_SPACE

        response = self._api_post("/valid_actions", {})
        if response and "actions" in response:
            return response["actions"]
        return self.ACTION_SPACE

    def render(self) -> np.ndarray:
        """获取游戏画面"""
        if not self.is_connected:
            return np.zeros((480, 640, 3), dtype=np.uint8)

        response = self._api_post("/render", {})
        if response and "image" in response:
            try:
                img_data = base64.b64decode(response["image"])
                return np.frombuffer(img_data, dtype=np.uint8).reshape(480, 640, 3)
            except:
                pass

        return np.zeros((480, 640, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取状态描述"""
        if self.current_state:
            return self.current_state
        return self._get_fallback_state()

    def _get_fallback_state(self) -> Dict[str, Any]:
        return {
            "grid": "API unavailable",
            "player_pos": (0, 0),
            "valid_actions": self.ACTION_SPACE,
            "steps": self.steps
        }

    def is_solvable(self) -> bool:
        return True


class Platformer2DEnv(Unity2DEnv):
    """
    平台跳跃游戏专用适配器
    继承自 Unity2DEnv，添加平台游戏特定的功能
    """

    def __init__(self, api_url: str = "http://localhost:8081", **kwargs):
        super().__init__(api_url, **kwargs)
        # 平台游戏特定的动作
        self.ACTION_SPACE = [
            'JUMP', 'DOUBLE_JUMP', 'DASH',
            'UP', 'DOWN', 'LEFT', 'RIGHT',
            'ATTACK', 'BLOCK'
        ]

    def get_state_description(self) -> Dict[str, Any]:
        """获取平台游戏特定的状态"""
        state = super().get_state_description()
        state["type"] = "platformer"
        return state


class Puzzle2DEnv(Unity2DEnv):
    """
    解谜游戏专用适配器
    """

    def __init__(self, api_url: str = "http://localhost:8081", **kwargs):
        super().__init__(api_url, **kwargs)
        self.ACTION_SPACE = [
            'INTERACT', 'USE_ITEM', 'INVENTORY',
            'UP', 'DOWN', 'LEFT', 'RIGHT'
        ]

    def get_state_description(self) -> Dict[str, Any]:
        state = super().get_state_description()
        state["type"] = "puzzle"
        return state
