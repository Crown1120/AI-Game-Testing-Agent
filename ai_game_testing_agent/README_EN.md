# AI Game Testing Agent

[中文](README.md) | [English](README_EN.md)

A smart game testing system built on LangGraph and LangChain that automates game testing through AI agents.

## Features

- **AI Test Agent**: Simulates player behavior to perform exploratory black-box testing and automatically discover bugs
- **AI Test Developer**: Analyzes bug reports and automatically generates pytest regression test code
- **Extensible Architecture**: Supports multiple game platforms through the `GameEnvironment` interface (Pygame, Unity, Web, PC, etc.)
- **Secure & Reliable**: Built-in timeout protection, retry mechanisms, and input validation

## Supported Game Platforms

| Platform | Status | Description |
|----------|--------|-------------|
| **Sokoban** | ✅ Built-in | Classic puzzle game for quick testing |
| **Unity 3D** | ✅ Supported | Via HTTP API or ML-Agents |
| **Unity 2D** | ✅ Supported | Platformer/Puzzle game support |
| **Web/H5 Games** | ✅ Supported | Selenium-based browser control |
| **WeChat Mini Games** | ✅ Supported | Airtest/Appium device control |
| **PC Desktop Games** | ✅ Supported | pyautogui image recognition + keyboard control |

## Architecture

```
ai_game_testing_agent/
├── game_env/              # Game Environment Adapters
│   ├── base_env.py       # Abstract base class
│   ├── sokoban_env.py    # Sokoban implementation
│   ├── unity3d_env.py    # Unity 3D adapter
│   ├── unity2d_env.py    # Unity 2D adapter
│   ├── web_game_env.py   # Web game adapter
│   ├── wechat_game_env.py # WeChat mini game adapter
│   └── pc_game_env.py    # PC game adapter
├── agent/                 # AI Agents
│   ├── state.py          # LangGraph state definitions
│   ├── tools.py          # Agent tools
│   ├── test_agent.py     # AI Test Agent (LangGraph)
│   └── dev_agent.py      # AI Test Developer (LangGraph)
├── utils/                 # Common utilities module
│   └── __init__.py       # Timeout handling, retry mechanisms, etc.
├── tests/                 # Test scenarios
├── data/                  # Reports and logs
├── main.py                # Main entry point
└── requirements.txt       # Dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
cd ai_game_testing_agent
pip install -r requirements.txt
```

### 2. Configure Environment

Copy `.env.example` to `.env` and fill in your API key:

```env
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.openai.com/v1
LLM_MODEL=gpt-4o
```

> ⚠️ **Security Note**: Never commit `.env` files containing real API keys to version control.

### 3. Run Tests

```bash
# Test Sokoban (built-in)
python main.py --env sokoban --steps 50

# Test Unity 3D game
python main.py --env unity3d --api-url http://localhost:8080 --steps 100

# Test Web game
python main.py --env web --game-url https://example.com --steps 100

# Test WeChat mini game
python main.py --env wechat --device android --steps 100

# Test PC game
python main.py --env pc --game-path "C:\Games\Game.exe" --steps 100
```

## Game Platform Details

### Sokoban (Built-in)

No additional setup required. Uses Pygame-based implementation.

```bash
python main.py --env sokoban --level default --steps 50
```

**Features**:
- BFS solvability verification (with timeout protection)
- Deadlock detection algorithm
- Configurable maximum steps

### Unity 3D Games

#### Unity Side Setup

1. Import the `.cs` files from `unity_server/` into your Unity project
2. Add the `UnityGameServer` component to a GameObject in your scene
3. Build and run your game

#### Python Side Configuration

```python
from game_env import Unity3DEnv

env = Unity3DEnv(
    api_url="http://localhost:8080",
    api_key=None  # Set if API key is configured in Unity
)
```

### Web/H5 Games

```python
from game_env import WebGameEnv

env = WebGameEnv(
    game_url="https://example.com/game.html",
    browser="chrome",
    headless=True
)
```

### WeChat Mini Games

Install additional dependencies:

```bash
pip install airtest appium-python-client
```

Usage:

```python
from game_env import WeChatMiniGameEnv

env = WeChatMiniGameEnv(
    game_name="Mini Game Name",
    device="android",  # or "ios"
    use_airtest=True
)
```

### PC Desktop Games

```python
from game_env import PCGameEnv

env = PCGameEnv(
    game_path="C:/Games/Game.exe",
    game_name="Game Name"
)
```

## Custom Game Environment

To test games on other platforms, extend the `GameEnvironment` base class:

```python
from game_env.base_env import GameEnvironment
from typing import Dict, List, Tuple, Any, Optional
import numpy as np

class MyGameEnv(GameEnvironment):
    def __init__(self, **kwargs):
        # Initialize your game connection
        pass

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        # Reset game logic
        return state

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        # Execute action
        return new_state, reward, done, info

    def get_valid_actions(self) -> List[str]:
        # Return valid actions for current state
        return actions

    def render(self) -> np.ndarray:
        # Return game screenshot
        return image

    def get_state_description(self) -> Dict[str, Any]:
        # Return state description for AI
        return state

    def is_solvable(self) -> bool:
        # Check if level is solvable
        return True
```

Then export in `game_env/__init__.py`:

```python
from .my_game_env import MyGameEnv

__all__ = [..., "MyGameEnv"]
```

## AI Agent Architecture

### Test Agent

The Test Agent uses LangGraph to create a state machine:

```
observe → decide → execute → validate → (continue? → observe : end)
```

1. **Observe**: Analyzes game state and plans next action
2. **Decide**: Selects action from valid actions
3. **Execute**: Performs the action in the game
4. **Validate**: Checks for anomalies and records bugs

### Dev Agent

The Dev Agent generates regression tests:

```
analyze → generate → validate → (save)
```

1. **Analyze**: Extracts failure patterns from bug reports
2. **Generate**: Creates pytest test code
3. **Validate**: Verifies Python syntax

### Common Utilities Module (utils)

Provides shared infrastructure:

- **Timeout Handling**: `invoke_with_timeout()` - Safe timeout control using ThreadPoolExecutor
- **Retry Mechanism**: `retry_with_backoff()` - Retry decorator with exponential backoff and jitter
- **Exception Types**: `TimeoutException`, `LLMInvocationError`

## Requirements

- Python 3.13+
- OpenAI API Key (or compatible LLM service)

### Core Dependencies

```
langgraph>=0.2.50
langchain>=0.3.0
langchain-openai>=0.2.0
pygame>=2.6.0
numpy>=2.0.0
python-dotenv>=1.0.0
```

### Optional Dependencies

```
# PC games
pyautogui>=0.9.50

# Web games
selenium>=4.15.0

# WeChat mini games
airtest>=1.3.0
appium-python-client>=4.0.0

# Unity ML-Agents (optional)
mlagents-envs>=0.28.0
```

## Project Structure

```
ai_game_testing_agent/
├── .env                    # Environment variables (not in Git)
├── .env.example           # Environment variable template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── requirements.txt       # Python dependencies
├── config.py              # Global configuration
├── main.py                # Main entry point
├── cli.py                 # CLI interface
├── game_env/              # Game environment adapters
│   ├── __init__.py
│   ├── base_env.py
│   └── [platform]_env.py
├── agent/                 # AI agents
│   ├── __init__.py
│   ├── state.py
│   ├── tools.py
│   ├── test_agent.py
│   └── dev_agent.py
├── utils/                 # Common utilities module
│   └── __init__.py
├── tests/                 # Test scenarios
│   ├── __init__.py
│   ├── test_scenarios.json
│   └── generated_tests/   # AI-generated tests
└── data/                  # Output data
    ├── reports/           # Test reports
    └── maps/              # Game maps
```

## Testing Workflow

1. **Initialization**: Game environment is initialized
2. **Exploration**: Test Agent explores the game for 50+ steps
3. **Bug Detection**: Anomalies are detected and recorded
4. **Report Generation**: Test report is saved to `data/reports/`
5. **Test Generation**: Dev Agent generates regression tests if bugs found
6. **Code Validation**: Generated code is syntax-checked

## Troubleshooting

### API Connection Failed

- Verify Unity game is running
- Check port configuration
- Check firewall settings

### LLM Call Timeout

System default timeout is 30 seconds, adjustable in `config.py`:

```python
TIMEOUT = 30  # LLM timeout in seconds
```

### Browser Driver Issues

```bash
pip install webdriver-manager
```

### Device Connection Issues (WeChat)

- Ensure device is connected and authorized
- Enable USB debugging
- Restart ADB: `adb kill-server && adb start-server`

## Changelog

### v1.1.0 (2026-04-14)

**Security Improvements**
- Enhanced API key validation, no longer prints sensitive information
- Unity server uses `[SerializeField] private` to protect API key
- HTTP server adds path validation to prevent injection attacks

**Performance Optimizations**
- BFS solvability verification with timeout protection (default 5 seconds)
- Reduced maximum search states to prevent memory exhaustion
- Replaced manual thread management with ThreadPoolExecutor

**Code Quality**
- Added `utils/` common module for unified timeout and retry logic
- Fixed stack overflow risk in recursive deadlock detection
- Extracted magic numbers to class constants
- Removed duplicate method definitions

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request
