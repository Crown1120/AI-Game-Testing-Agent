import os
import pygame
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from collections import deque
import copy

from .base_env import GameEnvironment

class SokobanEnv(GameEnvironment):
    """基于 Pygame 的推箱子游戏模拟器"""

    # 游戏元素映射: 0空地, 1墙, 2目标点, 3箱子在目标上, 4玩家, 5玩家在目标上, 6箱子
    TILE_MAPPING = {
        0: ' ', 1: '#', 2: '.', 3: '*', 4: '@', 5: '+', 6: '$'
    }
    ACTION_SPACE = ['UP', 'DOWN', 'LEFT', 'RIGHT']
    DIRECTION_DELTA = {
        'UP': (-1, 0),
        'DOWN': (1, 0),
        'LEFT': (0, -1),
        'RIGHT': (0, 1)
    }

    # 渲染颜色常量
    COLORS = {
        'empty': (255, 255, 255),      # 空地
        'wall': (100, 100, 100),       # 墙
        'goal': (255, 200, 200),       # 目标点
        'box_on_goal': (200, 150, 50), # 箱子在目标上
        'player': (0, 0, 255),         # 玩家
        'player_on_goal': (0, 255, 0), # 玩家在目标上
        'box': (139, 69, 19)           # 箱子
    }

    # 默认配置
    DEFAULT_MAX_STEPS = 500
    DEFAULT_CELL_SIZE = 64

    def __init__(self, map_file: Optional[str] = None, render_mode: str = "text", max_steps: int = None):
        self.map_data = None
        self.player_pos = None
        self.boxes = set()
        self.goals = set()
        self.steps = 0
        self.max_steps = max_steps if max_steps is not None else self.DEFAULT_MAX_STEPS
        self.render_mode = render_mode
        self.screen = None
        self.cell_size = self.DEFAULT_CELL_SIZE

        # 默认简单地图 (5x5)
        self.default_map = [
            "#####",
            "#@$.#",
            "#####"
        ]

        if map_file:
            self.load_map(map_file)
        else:
            self._load_from_strings(self.default_map)

        if render_mode == "human":
            pygame.init()
            self.screen = pygame.display.set_mode(
                (len(self.map_data[0]) * self.cell_size, len(self.map_data) * self.cell_size)
            )
            pygame.display.set_caption("Sokoban - AI Testing")

    def _load_from_strings(self, map_strings: List[str]):
        """从字符串列表解析地图"""
        self.map_data = []
        self.boxes = set()
        self.goals = set()
        for r, line in enumerate(map_strings):
            row = []
            for c, ch in enumerate(line):
                if ch == '#':
                    row.append(1)
                elif ch == '.':
                    row.append(2)
                    self.goals.add((r, c))
                elif ch == '*':
                    row.append(3)
                    self.boxes.add((r, c))
                    self.goals.add((r, c))
                elif ch == '@':
                    row.append(4)
                    self.player_pos = (r, c)
                elif ch == '+':
                    row.append(5)
                    self.player_pos = (r, c)
                    self.goals.add((r, c))
                elif ch == '$':
                    row.append(6)
                    self.boxes.add((r, c))
                else:
                    row.append(0)
            self.map_data.append(row)

    def load_map(self, file_path: str):
        """从文件加载地图"""
        with open(file_path, 'r') as f:
            lines = [line.rstrip('\n') for line in f if line.strip()]
        self._load_from_strings(lines)

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置环境"""
        if level_id and level_id != "default":
            map_path = f"data/maps/{level_id}.txt"
            if os.path.exists(map_path):
                self.load_map(map_path)
        else:
            self._load_from_strings(self.default_map)
        self.steps = 0
        return self.get_state_description()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        self.steps += 1
        reward = 0.0
        info = {"success": False, "box_moved": False}

        if action not in self.ACTION_SPACE:
            info["error"] = f"Invalid action: {action}"
            return self.get_state_description(), reward, self._is_done(), info

        dr, dc = self.DIRECTION_DELTA[action]
        r, c = self.player_pos
        nr, nc = r + dr, c + dc

        # 检查墙壁
        if self.map_data[nr][nc] == 1:
            info["error"] = "Hit wall"
            return self.get_state_description(), -0.1, self._is_done(), info

        # 检查箱子
        if (nr, nc) in self.boxes:
            nnr, nnc = nr + dr, nc + dc
            if self.map_data[nnr][nnc] == 1 or (nnr, nnc) in self.boxes:
                info["error"] = "Cannot push box"
                return self.get_state_description(), -0.1, self._is_done(), info
            # 移动箱子
            self.boxes.remove((nr, nc))
            self.boxes.add((nnr, nnc))
            info["box_moved"] = True
            reward = 1.0 if (nnr, nnc) in self.goals else 0.2

        # 移动玩家
        self.player_pos = (nr, nc)
        info["success"] = True

        state = self.get_state_description()
        done = self._is_done()
        if done and self._all_boxes_on_goals():
            reward = 10.0
        elif self.steps >= self.max_steps:
            done = True
            reward = -1.0

        return state, reward, done, info

    def get_valid_actions(self) -> List[str]:
        """返回当前状态下合法的动作"""
        valid = []
        for action in self.ACTION_SPACE:
            dr, dc = self.DIRECTION_DELTA[action]
            r, c = self.player_pos
            nr, nc = r + dr, c + dc
            if self.map_data[nr][nc] != 1:
                if (nr, nc) in self.boxes:
                    nnr, nnc = nr + dr, nc + dc
                    if self.map_data[nnr][nnc] != 1 and (nnr, nnc) not in self.boxes:
                        valid.append(action)
                else:
                    valid.append(action)
        return valid

    def render(self) -> np.ndarray:
        """渲染当前画面为numpy数组"""
        if self.render_mode == "human" and self.screen:
            self._render_pygame()
            pygame.display.flip()
        # 返回伪图像数据（实际可使用 pygame.surfarray.array3d）
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def _render_pygame(self):
        """Pygame 渲染"""
        for r in range(len(self.map_data)):
            for c in range(len(self.map_data[0])):
                tile = self.map_data[r][c]
                # 根据瓦片类型选择颜色
                if tile == 1:
                    color = self.COLORS['wall']
                elif tile == 2:
                    color = self.COLORS['goal']
                elif tile == 3:
                    color = self.COLORS['box_on_goal']
                elif tile == 4:
                    color = self.COLORS['player']
                elif tile == 5:
                    color = self.COLORS['player_on_goal']
                else:
                    color = self.COLORS['empty']

                pygame.draw.rect(self.screen, color,
                                 (c*self.cell_size, r*self.cell_size, self.cell_size, self.cell_size))
                if (r, c) in self.boxes:
                    pygame.draw.circle(self.screen, self.COLORS['box'],
                                       (c*self.cell_size+32, r*self.cell_size+32), 20)
                if (r, c) == self.player_pos:
                    pygame.draw.circle(self.screen, self.COLORS['player'],
                                       (c*self.cell_size+32, r*self.cell_size+32), 20)

    def get_state_description(self) -> Dict[str, Any]:
        """返回文本形式的状态描述（增强版，包含更多AI友好的信息）"""
        rows = len(self.map_data)
        cols = len(self.map_data[0])
        grid = [[' ' for _ in range(cols)] for _ in range(rows)]
        for r in range(rows):
            for c in range(cols):
                if self.map_data[r][c] == 1:
                    grid[r][c] = '#'
                elif (r, c) in self.goals:
                    grid[r][c] = '.'
        for box in self.boxes:
            grid[box[0]][box[1]] = '*' if box in self.goals else '$'
        pr, pc = self.player_pos
        grid[pr][pc] = '+' if (pr, pc) in self.goals else '@'

        grid_str = '\n'.join(''.join(row) for row in grid)

        # 计算箱子到目标点的曼哈顿距离
        box_distances = []
        for box in self.boxes:
            min_dist = min(abs(box[0] - g[0]) + abs(box[1] - g[1]) for g in self.goals)
            box_distances.append(min_dist)

        # 检测潜在问题
        issues = []
        if self.steps >= self.max_steps * 0.8:
            issues.append("warning: near_max_steps")
        if len(self.get_valid_actions()) == 0:
            issues.append("error: no_valid_actions")

        return {
            "grid": grid_str,
            "player_pos": self.player_pos,
            "boxes": list(self.boxes),
            "goals": list(self.goals),
            "steps": self.steps,
            "max_steps": self.max_steps,
            "boxes_on_goal": sum(1 for box in self.boxes if box in self.goals),
            "total_goals": len(self.goals),
            "total_boxes": len(self.boxes),
            "valid_actions": self.get_valid_actions(),
            "box_distances_to_goals": box_distances,
            "avg_distance_to_goal": sum(box_distances) / len(box_distances) if box_distances else 0,
            "progress": sum(1 for box in self.boxes if box in self.goals) / len(self.goals) if self.goals else 0,
            "issues": issues,
            "map_info": self.get_map_info()
        }

    def get_map_info(self) -> Dict[str, Any]:
        """获取地图详细信息"""
        walls = []
        empty = []
        for r in range(len(self.map_data)):
            for c in range(len(self.map_data[0])):
                if self.map_data[r][c] == 1:
                    walls.append((r, c))
                else:
                    empty.append((r, c))

        return {
            "width": len(self.map_data[0]) if self.map_data else 0,
            "height": len(self.map_data) if self.map_data else 0,
            "total_tiles": len(self.map_data) * len(self.map_data[0]) if self.map_data else 0,
            "walls_count": len(walls),
            "empty_tiles_count": len(empty),
            "is_solvable": self.is_solvable()
        }

    def _all_boxes_on_goals(self) -> bool:
        """检查是否所有箱子都在目标点上"""
        return all(box in self.goals for box in self.boxes)

    def _is_done(self) -> bool:
        """游戏是否结束"""
        return self._all_boxes_on_goals() or self.steps >= self.max_steps

    def is_solvable(self, timeout_seconds: float = 5.0) -> bool:
        """使用BFS检查当前关卡是否可解

        算法：从初始状态开始BFS搜索，直到找到所有箱子都在目标点的状态
        状态：(玩家位置, 箱子位置集合)

        Args:
            timeout_seconds: 搜索超时时间（秒），默认5秒
        """
        import time
        start_time = time.time()

        if not self.goals or not self.boxes:
            return False

        # 检查箱子数量是否等于目标点数量
        if len(self.boxes) != len(self.goals):
            return False

        # 检查箱子是否被卡在死胡同（不在目标点上）
        for box in self.boxes:
            if box not in self.goals:
                if self._is_box_in_deadlock(box):
                    return False

        # BFS 搜索
        initial_state = (self.player_pos, frozenset(self.boxes))
        visited = {initial_state}
        queue = deque([(initial_state, [])])

        max_states = 50000  # 降低最大状态数，防止内存耗尽
        states_explored = 0

        while queue:
            # 超时检查
            if time.time() - start_time > timeout_seconds:
                print(f"⚠ BFS 搜索超时（>{timeout_seconds}秒），已探索 {states_explored} 个状态")
                return False

            if states_explored > max_states:
                print(f"⚠ BFS 达到最大状态数限制 ({max_states})")
                break
            states_explored += 1

            (player_pos, boxes), path = queue.popleft()

            # 检查是否完成
            if boxes == frozenset(self.goals):
                return True

            # 尝试每个方向
            for action in self.ACTION_SPACE:
                dr, dc = self.DIRECTION_DELTA[action]
                pr, pc = player_pos
                nr, nc = pr + dr, pc + dc

                # 检查是否是墙
                if self._is_wall(nr, nc):
                    continue

                new_boxes = boxes
                box_moved = False

                # 检查是否推箱子
                if (nr, nc) in boxes:
                    bnr, bnc = nr + dr, nc + dc
                    # 箱子后面是墙或另一个箱子
                    if self._is_wall(bnr, bnc) or (bnr, bnc) in boxes:
                        continue
                    # 移动箱子
                    new_boxes = boxes - {(nr, nc)} | {(bnr, bnc)}
                    box_moved = True

                new_player_pos = (nr, nc)
                new_state = (new_player_pos, frozenset(new_boxes))

                if new_state not in visited:
                    visited.add(new_state)
                    new_path = path + [action]
                    queue.append((new_state, new_path))

        return False

    def _is_wall(self, r: int, c: int) -> bool:
        """检查位置是否是墙"""
        if 0 <= r < len(self.map_data) and 0 <= c < len(self.map_data[0]):
            return self.map_data[r][c] == 1
        return True

    def _is_box_in_deadlock(self, box: Tuple[int, int], visited: set = None) -> bool:
        """检查箱子是否在死胡同（无法移动到目标点）

        Args:
            box: 要检查的箱子位置
            visited: 已访问的箱子集合，防止循环递归
        """
        if visited is None:
            visited = set()

        # 防止循环递归
        if box in visited:
            return False
        visited.add(box)

        r, c = box

        # 如果箱子已经在目标点上，不是死锁
        if box in self.goals:
            return False

        # 检查四个方向是否都被墙或死锁位置包围
        walls_count = 0
        for dr, dc in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            nr, nc = r + dr, c + dc
            if self._is_wall(nr, nc):
                walls_count += 1
            elif (nr, nc) in self.boxes:
                # 另一个箱子，检查它是否也是死锁
                if self._is_box_in_deadlock((nr, nc), visited):
                    walls_count += 1

        # 如果三个方向都被阻挡，箱子被卡住
        return walls_count >= 3

    def get_all_levels(self) -> List[str]:
        """获取所有可用关卡ID"""
        levels = []
        maps_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "maps")
        if os.path.exists(maps_dir):
            for f in os.listdir(maps_dir):
                if f.endswith('.txt'):
                    levels.append(f.replace('.txt', ''))
        return sorted(levels)
