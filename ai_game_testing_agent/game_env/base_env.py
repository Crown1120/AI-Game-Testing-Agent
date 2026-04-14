from abc import ABC, abstractmethod
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

class GameEnvironment(ABC):
    """所有游戏环境必须实现的统一接口"""

    @abstractmethod
    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏环境到指定关卡，返回初始状态"""
        pass

    @abstractmethod
    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行一个动作，返回 (新状态, 奖励值, 是否结束, 额外信息)"""
        pass

    @abstractmethod
    def get_valid_actions(self) -> List[str]:
        """返回当前状态下所有合法动作的列表"""
        pass

    @abstractmethod
    def render(self) -> np.ndarray:
        """以numpy数组（RGB图像）的形式返回游戏当前画面的截图"""
        pass

    @abstractmethod
    def get_state_description(self) -> Dict[str, Any]:
        """返回当前游戏状态的文本描述，供LLM理解上下文"""
        pass

    @abstractmethod
    def is_solvable(self) -> bool:
        """验证当前关卡是否存在可行解（通常使用BFS算法）"""
        pass
