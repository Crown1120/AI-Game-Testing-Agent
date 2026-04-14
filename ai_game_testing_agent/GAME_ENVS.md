# AI Game Testing Agent - 游戏环境文档

## 支持的游戏平台

### 1. 推箱子 (Sokoban) - 内置
```bash
python main.py --env sokoban --level default --steps 50
```

### 2. Unity 3D 游戏
```bash
python main.py --env unity3d --api-url http://localhost:8080 --steps 100
```

需要在 Unity 侧实现 HTTP API 服务器，支持以下端点：
- `GET /status` - 获取服务器状态
- `POST /reset` - 重置游戏
- `POST /step` - 执行动作
- `POST /valid_actions` - 获取合法动作
- `POST /render` - 获取屏幕截图

### 3. Unity 2D 游戏
```bash
python main.py --env unity2d --api-url http://localhost:8081 --steps 100
```

支持子类型：
- `Platformer2DEnv` - 平台跳跃游戏
- `Puzzle2DEnv` - 解谜游戏

### 4. Web 游戏 / H5 游戏
```bash
python main.py --env web --game-url https://example.com/game.html --steps 100
```

使用 Selenium 控制浏览器，适用于所有网页游戏。

### 5. 微信小游戏
```bash
python main.py --env wechat --device android --steps 100
```

需要：
- 安装 Airtest 或 Appium
- 连接 Android 设备或 iOS 设备
- 微信已登录

### 6. PC 桌面游戏
```bash
python main.py --env pc --game-path "C:\Games\Game.exe" --steps 100
```

使用 pyautogui 控制鼠标键盘，适用于任何 Windows 桌面游戏。

## 安装额外依赖

```bash
# PC 游戏支持
pip install pyautogui

# Web 游戏支持
pip install selenium

# 微信小游戏支持
pip install airtest appium-python-client

# ML-Agents 支持（可选）
pip install mlagents-envs
```

## 添加新的游戏环境

1. 在 `game_env/` 目录下创建新文件（如 `my_game_env.py`）
2. 继承 `GameEnvironment` 基类
3. 实现所有抽象方法
4. 在 `game_env/__init__.py` 中导出新类
5. 在 `GAME_ENVIRONMENTS` 注册表中注册
