"""
Unity 3D 游戏环境适配器
支持通过 HTTP API 或 ML-Agents 连接 Unity 游戏
"""
import requests
import json
import time
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

from .base_env import GameEnvironment


class Unity3DEnv(GameEnvironment):
    """
    Unity 3D 游戏环境适配器

    支持两种连接方式：
    1. HTTP API 模式：Unity 侧运行 Web API 服务器
    2. ML-Agents 模式：使用 Unity ML-Agents SDK

    需要在 Unity 侧实现对应的 API 接口
    """

    def __init__(
        self,
        api_url: str = "http://localhost:8080",
        api_key: str = None,
        render_mode: str = "text",
        timeout: int = 10
    ):
        """
        初始化 Unity 3D 环境

        Args:
            api_url: Unity API 服务器地址
            api_key: API 认证密钥（可选）
            render_mode: 渲染模式 ('text' 或 'human')
            timeout: 请求超时时间（秒）
        """
        self.api_url = api_url.rstrip('/')
        self.api_key = api_key
        self.render_mode = render_mode
        self.timeout = timeout
        self.current_state = None
        self.is_connected = False

        # 动作空间定义（可根据具体游戏修改）
        self.ACTION_SPACE = [
            'MOVE_FORWARD', 'MOVE_BACKWARD', 'MOVE_LEFT', 'MOVE_RIGHT',
            'LOOK_UP', 'LOOK_DOWN', 'LOOK_LEFT', 'LOOK_RIGHT',
            'JUMP', 'CROUCH', 'ATTACK', 'INTERACT', 'NONE'
        ]

        # 尝试连接
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
                self.is_connected = True
                print(f"✓ 已连接到 Unity 3D 游戏: {response.json()}")
        except Exception as e:
            print(f"⚠ 连接 Unity API 失败: {e}")
            print("  请确保 Unity 游戏已启动并运行 API 服务器")
            print("  参考: https://github.com/yourname/unity-game-api")

    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        return headers

    def _api_post(self, endpoint: str, data: Dict[str, Any]) -> Optional[Dict]:
        """发送 API 请求"""
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
            print(f"API 请求失败: {e}")
        return None

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏到初始状态或指定关卡"""
        data = {"level_id": level_id} if level_id else {}
        response = self._api_post("/reset", data)

        if response:
            self.current_state = response.get("state", {})
            return self.get_state_description()
        return self._get_fallback_state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行一个动作"""
        if not self.is_connected:
            return self._get_fallback_state(), 0.0, True, {"error": "Not connected"}

        response = self._api_post("/step", {"action": action})

        if response:
            new_state = response.get("state", {})
            reward = response.get("reward", 0.0)
            done = response.get("done", False)
            info = response.get("info", {})

            self.current_state = new_state
            return new_state, reward, done, info

        # API 失败时返回默认值
        return self._get_fallback_state(), 0.0, True, {"error": "API failed"}

    def get_valid_actions(self) -> List[str]:
        """获取当前状态下合法的动作列表"""
        if not self.is_connected:
            return self.ACTION_SPACE

        response = self._api_post("/valid_actions", {})
        if response and "actions" in response:
            return response["actions"]
        return self.ACTION_SPACE

    def render(self) -> np.ndarray:
        """获取游戏画面截图"""
        if not self.is_connected:
            return np.zeros((100, 100, 3), dtype=np.uint8)

        response = self._api_post("/render", {})
        if response and "image" in response:
            # 如果返回 base64 图像，需要解码
            import base64
            img_data = base64.b64decode(response["image"])
            return np.frombuffer(img_data, dtype=np.uint8).reshape(100, 100, 3)

        # 返回空图像作为占位
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取当前游戏状态的文本描述"""
        if self.current_state:
            return self.current_state

        return self._get_fallback_state()

    def _get_fallback_state(self) -> Dict[str, Any]:
        """获取默认状态（API 失败时使用）"""
        return {
            "grid": "API unavailable - using fallback mode",
            "player_pos": (0, 0, 0),
            "valid_actions": self.ACTION_SPACE,
            "steps": 0
        }

    def is_solvable(self) -> bool:
        """验证关卡是否可解（简化版）"""
        # 实际实现需要根据具体游戏逻辑
        return True


class Unity3DMLAgentsEnv(GameEnvironment):
    """
    使用 Unity ML-Agents 的游戏环境适配器

    需要安装: pip install mlagents-envs
    """

    def __init__(self, env_path: str = None, render_mode: str = "text"):
        """
        初始化 ML-Agents 环境

        Args:
            env_path: Unity 环境可执行文件路径
            render_mode: 渲染模式
        """
        self.env_path = env_path
        self.render_mode = render_mode
        self.env = None
        self._initialize_env()

    def _initialize_env(self):
        """初始化 ML-Agents 环境"""
        try:
            from mlagents_envs.environment import UnityEnvironment
            self.env = UnityEnvironment(file_name=self.env_path)
            self.env.reset()
            print("✓ ML-Agents 环境初始化成功")
        except ImportError:
            print("⚠ 未安装 mlagents-envs: pip install mlagents-envs")
        except Exception as e:
            print(f"⚠ ML-Agents 初始化失败: {e}")

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置环境"""
        if self.env:
            self.env.reset()
            return self._get_state_from_brain()
        return {}

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        if not self.env:
            return {}, 0.0, True, {}

        # 将字符串动作转换为 ML-Agents 动作
        # 这里需要根据具体游戏的动作空间进行映射
        actions = self._action_to_continuous(action)

        self.env.step(actions)
        return self._get_state_from_brain(), 0.0, False, {}

    def get_valid_actions(self) -> List[str]:
        """获取合法动作"""
        if self.env:
            brain_name = self.env.brain_names[0]
            brain = self.env.brains[brain_name]
            # 根据 brain.action_space 获取合法动作
        return ['UP', 'DOWN', 'LEFT', 'RIGHT']

    def render(self) -> np.ndarray:
        """渲染环境"""
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取状态描述"""
        return self._get_state_from_brain()

    def _get_state_from_brain(self) -> Dict[str, Any]:
        """从 brain 获取状态"""
        brain_name = self.env.brain_names[0]
        brain_info = self.env.brains[brain_name]
        return {"brain_info": str(brain_info)}

    def _action_to_continuous(self, action: str) -> List[float]:
        """将字符串动作转换为连续动作向量"""
        # 根据具体游戏的动作空间实现
        return [0.0, 0.0]

    def is_solvable(self) -> bool:
        return True
