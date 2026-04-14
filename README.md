# AI Game Testing Agent

[中文](ai_game_testing_agent/README.md) | [English](ai_game_testing_agent/README_EN.md)

基于 LangGraph 和 LangChain 构建的智能游戏测试系统，通过 AI 代理自动化游戏测试。

## 快速开始

```bash
cd ai_game_testing_agent
pip install -r requirements.txt
cp .env.example .env
# 编辑 .env 填写 API Key
python main.py --env sokoban --steps 50
```

## 支持的平台

| 平台 | 状态 |
|------|------|
| 推箱子 (内置) | ✅ |
| Unity 3D/2D | ✅ |
| Web/H5 游戏 | ✅ |
| 微信小游戏 | ✅ |
| PC 桌面游戏 | ✅ |

## 项目结构

```
├── ai_game_testing_agent/    # Python 主项目
│   ├── agent/               # AI 代理
│   ├── game_env/            # 游戏环境适配器
│   ├── utils/               # 公共工具
│   └── ...
└── unity_server/            # Unity 服务端脚本
```

## 许可证

[MIT License](LICENSE)
