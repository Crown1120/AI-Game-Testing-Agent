# AI 游戏测试助手

[中文](README.md) | [English](README_EN.md)

基于 LangGraph 和 LangChain 构建的智能游戏测试系统，通过 AI 代理自动化游戏测试。

## 功能特性

- **AI 测试代理**：模拟玩家行为进行探索性黑盒测试，自动发现游戏漏洞
- **AI 测试开发**：分析漏洞报告，自动生成 pytest 回归测试代码
- **可扩展架构**：通过 `GameEnvironment` 接口支持多种游戏平台（Pygame、Unity、Web、PC 等）
- **安全可靠**：内置超时保护、重试机制和输入验证

## 支持的游戏平台

| 平台 | 状态 | 描述 |
|------|------|------|
| **推箱子 (Sokoban)** | ✅ 内置 | 经典益智游戏，用于快速测试 |
| **Unity 3D** | ✅ 支持 | 通过 HTTP API 或 ML-Agents |
| **Unity 2D** | ✅ 支持 | 平台/益智游戏支持 |
| **Web/H5 游戏** | ✅ 支持 | 基于 Selenium 的浏览器控制 |
| **微信小游戏** | ✅ 支持 | Airtest/Appium 设备控制 |
| **PC 桌面游戏** | ✅ 支持 | pyautogui 图像识别 + 键盘控制 |

## 架构图

```
ai_game_testing_agent/
├── game_env/              # 游戏环境适配器
│   ├── base_env.py       # 抽象基类
│   ├── sokoban_env.py    # 推箱子实现
│   ├── unity3d_env.py    # Unity 3D 适配器
│   ├── unity2d_env.py    # Unity 2D 适配器
│   ├── web_game_env.py   # Web 游戏适配器
│   ├── wechat_game_env.py # 微信小游戏适配器
│   └── pc_game_env.py    # PC 游戏适配器
├── agent/                 # AI 代理
│   ├── state.py          # LangGraph 状态定义
│   ├── tools.py          # 代理工具
│   ├── test_agent.py     # AI 测试代理 (LangGraph)
│   └── dev_agent.py      # AI 测试开发 (LangGraph)
├── utils/                 # 公共工具模块
│   └── __init__.py       # 超时处理、重试机制等
├── tests/                 # 测试场景
├── data/                  # 报告和日志
├── main.py                # 主入口点
└── requirements.txt       # 依赖项
```

## 快速开始

### 1. 安装依赖

```bash
cd ai_game_testing_agent
pip install -r requirements.txt
```

### 2. 配置环境

复制 `.env.example` 到 `.env` 并填写您的 API 密钥：

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
```

> ⚠️ **安全提示**：请勿将包含真实 API Key 的 `.env` 文件提交到版本控制系统。

### 3. 运行测试

```bash
# 测试推箱子（内置）
python main.py --env sokoban --steps 50

# 测试 Unity 3D 游戏
python main.py --env unity3d --api-url http://localhost:8080 --steps 100

# 测试 Web 游戏
python main.py --env web --game-url https://example.com --steps 100

# 测试微信小游戏
python main.py --env wechat --device android --steps 100

# 测试 PC 游戏
python main.py --env pc --game-path "C:\Games\Game.exe" --steps 100
```

## 游戏平台详情

### 推箱子（内置）

无需额外设置，使用基于 Pygame 的实现。

```bash
python main.py --env sokoban --level default --steps 50
```

**特性**：
- BFS 可解性验证（带超时保护）
- 死锁检测算法
- 可配置的最大步数

### Unity 3D 游戏

#### Unity 端设置

1. 将 `unity_server/` 目录中的 `.cs` 文件导入到您的 Unity 项目中
2. 在场景中的 GameObject 上添加 `UnityGameServer` 组件
3. 构建并运行您的游戏

#### Python 端配置

```python
from game_env import Unity3DEnv

env = Unity3DEnv(
    api_url="http://localhost:8080",
    api_key=None  # 如果在 Unity 中配置了 API 密钥，请设置
)
```

### Web/H5 游戏

```python
from game_env import WebGameEnv

env = WebGameEnv(
    game_url="https://example.com/game.html",
    browser="chrome",
    headless=True
)
```

### 微信小游戏

安装额外依赖：

```bash
pip install airtest appium-python-client
```

使用方法：

```python
from game_env import WeChatMiniGameEnv

env = WeChatMiniGameEnv(
    game_name="小游戏名称",
    device="android",  # 或 "ios"
    use_airtest=True
)
```

### PC 桌面游戏

```python
from game_env import PCGameEnv

env = PCGameEnv(
    game_path="C:/Games/Game.exe",
    game_name="游戏名称"
)
```

## 自定义游戏环境

要测试其他平台的游戏，请扩展 `GameEnvironment` 基类：

```python
from game_env.base_env import GameEnvironment
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

class MyGameEnv(GameEnvironment):
    def __init__(self, **kwargs):
        # 初始化您的游戏连接
        pass

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        # 重置游戏逻辑
        return state

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        # 执行动作
        return new_state, reward, done, info

    def get_valid_actions(self) -> List[str]:
        # 返回当前状态的有效动作
        return actions

    def render(self) -> np.ndarray:
        # 返回游戏截图
        return image

    def get_state_description(self) -> Dict[str, Any]:
        # 返回 AI 的状态描述
        return state

    def is_solvable(self) -> bool:
        # 检查关卡是否可解
        return True
```

然后在 `game_env/__init__.py` 中导出：

```python
from .my_game_env import MyGameEnv

__all__ = [..., "MyGameEnv"]
```

## AI 代理架构

### 测试代理 (Test Agent)

测试代理使用 LangGraph 创建状态机：

```
观察 → 决策 → 执行 → 验证 → (继续? → 观察 : 结束)
```

1. **观察**：分析游戏状态并规划下一步动作
2. **决策**：从有效动作中选择动作
3. **执行**：在游戏中执行动作
4. **验证**：检查异常并记录漏洞

### 开发代理 (Dev Agent)

开发代理生成回归测试：

```
分析 → 生成 → 验证 → (保存)
```

1. **分析**：从漏洞报告中提取失败模式
2. **生成**：创建 pytest 测试代码
3. **验证**：验证 Python 语法

### 公共工具模块 (utils)

提供共享的基础设施：

- **超时处理**：`invoke_with_timeout()` - 使用 ThreadPoolExecutor 实现安全的超时控制
- **重试机制**：`retry_with_backoff()` - 带指数退避和抖动的重试装饰器
- **异常类型**：`TimeoutException`、`LLMInvocationError`

## 依赖要求

- Python 3.13+
- OpenAI API 密钥（或兼容的 LLM 服务）

### 核心依赖

```
langgraph>=0.2.50
langchain>=0.3.0
langchain-openai>=0.2.0
pygame>=2.6.0
numpy>=2.0.0
python-dotenv>=1.0.0
```

### 可选依赖

```
# PC 游戏
pyautogui>=0.9.50

# Web 游戏
selenium>=4.15.0

# 微信小游戏
airtest>=1.3.0
appium-python-client>=4.0.0

# Unity ML-Agents（可选）
mlagents-envs>=0.28.0
```

## 项目结构

```
ai_game_testing_agent/
├── .env                    # 环境变量（不在 Git 中）
├── .env.example           # 环境变量模板
├── .gitignore             # Git 忽略规则
├── README.md              # 本文件
├── requirements.txt       # Python 依赖
├── config.py              # 全局配置
├── main.py                # 主入口点
├── cli.py                 # CLI 接口
├── game_env/              # 游戏环境适配器
│   ├── __init__.py
│   ├── base_env.py
│   └── [平台]_env.py
├── agent/                 # AI 代理
│   ├── __init__.py
│   ├── state.py
│   ├── tools.py
│   ├── test_agent.py
│   └── dev_agent.py
├── utils/                 # 公共工具模块
│   └── __init__.py
├── tests/                 # 测试场景
│   ├── __init__.py
│   ├── test_scenarios.json
│   └── generated_tests/   # AI 生成的测试
└── data/                  # 输出数据
    ├── reports/           # 测试报告
    └── maps/              # 游戏地图
```

## 测试工作流程

1. **初始化**：初始化游戏环境
2. **探索**：测试代理探索游戏 50+ 步
3. **漏洞检测**：检测并记录异常
4. **报告生成**：测试报告保存到 `data/reports/`
5. **测试生成**：如果发现漏洞，开发代理生成回归测试
6. **代码验证**：生成的代码进行语法检查

## 故障排除

### API 连接失败

- 确认 Unity 游戏正在运行
- 检查端口配置
- 检查防火墙设置

### LLM 调用超时

系统默认 30 秒超时，可在 `config.py` 中调整：

```python
TIMEOUT = 30  # LLM 超时秒数
```

### 浏览器驱动问题

```bash
pip install webdriver-manager
```

### 设备连接问题（微信）

- 确保设备已连接并授权
- 启用 USB 调试
- 重启 ADB：`adb kill-server && adb start-server`

## 更新日志

### v1.1.0 (2026-04-14)

**安全性改进**
- API Key 验证增强，不再打印敏感信息
- Unity 服务器使用 `[SerializeField] private` 保护 API Key
- HTTP 服务器添加路径验证，防止注入攻击

**性能优化**
- BFS 可解性验证添加超时保护（默认 5 秒）
- 降低最大搜索状态数，防止内存耗尽
- 使用 ThreadPoolExecutor 替代手动线程管理

**代码质量**
- 新增 `utils/` 公共模块，统一超时和重试逻辑
- 修复递归死锁检测的栈溢出风险
- 提取魔法数字为类常量
- 删除重复的方法定义

## 许可证

MIT 许可证

## 贡献

欢迎贡献！欢迎提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的修改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启 Pull Request
