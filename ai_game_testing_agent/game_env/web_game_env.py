"""
Web 游戏环境适配器
支持通过 Selenium 或 Playwright 控制浏览器游戏
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import time

from .base_env import GameEnvironment


class WebGameEnv(GameEnvironment):
    """
    Web 游戏环境适配器

    支持通过 Selenium 或 Playwright 控制浏览器游戏
    适用于网页游戏、H5 游戏等
    """

    def __init__(
        self,
        game_url: str = None,
        browser: str = "chrome",
        headless: bool = True,
        render_mode: str = "text"
    ):
        """
        初始化 Web 游戏环境

        Args:
            game_url: 游戏 URL
            browser: 浏览器类型 ('chrome' 或 'firefox')
            headless: 无头模式
            render_mode: 渲染模式
        """
        self.game_url = game_url
        self.browser = browser
        self.headless = headless
        self.render_mode = render_mode
        self.driver = None
        self.is_connected = False

        self._initialize_driver()

    def _initialize_driver(self):
        """初始化浏览器驱动"""
        try:
            if self.browser == "chrome":
                from selenium import webdriver
                from selenium.webdriver.chrome.options import Options

                options = Options()
                if self.headless:
                    options.add_argument('--headless')
                options.add_argument('--no-sandbox')
                options.add_argument('--disable-dev-shm-usage')

                self.driver = webdriver.Chrome(options=options)
            elif self.browser == "firefox":
                from selenium import webdriver
                from selenium.webdriver.firefox.options import Options

                options = Options()
                if self.headless:
                    options.add_argument('--headless')

                self.driver = webdriver.Firefox(options=options)
            else:
                from selenium import webdriver

                self.driver = webdriver.Chrome()

            self.driver.set_window_size(1920, 1080)
            print(f"✓ 浏览器驱动初始化成功")
            self.is_connected = True

        except ImportError:
            print("⚠ 未安装 selenium: pip install selenium")
        except Exception as e:
            print(f"⚠ 浏览器驱动初始化失败: {e}")

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            if self.game_url:
                self.driver.get(self.game_url)
                time.sleep(2)  # 等待页面加载

            return self.get_state_description()
        except Exception as e:
            print(f"重置失败: {e}")
            return self._get_fallback_state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        if not self.is_connected:
            return self._get_fallback_state(), 0.0, True, {"error": "Not connected"}

        try:
            # 执行动作
            self._execute_action(action)
            time.sleep(0.1)  # 等待游戏状态更新

            new_state = self.get_state_description()
            return new_state, 0.0, False, {}
        except Exception as e:
            print(f"执行动作失败: {e}")
            return self._get_fallback_state(), 0.0, True, {"error": str(e)}

    def get_valid_actions(self) -> List[str]:
        """获取合法动作"""
        # 可以通过分析页面元素来动态获取合法动作
        if not self.is_connected:
            return ['UP', 'DOWN', 'LEFT', 'RIGHT', 'CLICK', 'KEY_PRESS']

        try:
            # 尝试从页面获取动作信息
            script = """
            return {
                'buttons': Array.from(document.querySelectorAll('button')).map(b => b.textContent),
                'keys': ['UP', 'DOWN', 'LEFT', 'RIGHT', 'SPACE', 'ENTER']
            }
            """
            result = self.driver.execute_script(script)
            return result.get('keys', ['UP', 'DOWN', 'LEFT', 'RIGHT'])
        except:
            pass

        return ['UP', 'DOWN', 'LEFT', 'RIGHT', 'CLICK', 'KEY_PRESS']

    def render(self) -> np.ndarray:
        """获取游戏画面截图"""
        if not self.is_connected:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

        try:
            # 截图
            screenshot = self.driver.get_screenshot_as_png()
            nparr = np.frombuffer(screenshot, dtype=np.uint8)
            return nparr.reshape(1080, 1920, 3)
        except Exception as e:
            print(f"截图失败: {e}")
            return np.zeros((1080, 1920, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            # 获取页面状态
            script = """
            return {
                'url': window.location.href,
                'title': document.title,
                'elements': Array.from(document.body.innerText).slice(0, 100).join('')
            }
            """
            state = self.driver.execute_script(script)
            state["screenshot_available"] = True
            return state
        except Exception as e:
            return self._get_fallback_state()

    def _execute_action(self, action: str):
        """执行具体动作"""
        from selenium.webdriver.common.keys import Keys

        action_map = {
            'UP': Keys.ARROW_UP,
            'DOWN': Keys.ARROW_DOWN,
            'LEFT': Keys.ARROW_LEFT,
            'RIGHT': Keys.ARROW_RIGHT,
            'JUMP': Keys.SPACE,
            'ATTACK': Keys.ENTER,
            'CLICK': None  # 需要特殊处理
        }

        key = action_map.get(action, None)
        if key:
            # 发送按键
            body = self.driver.find_element("tag name", "body")
            body.send_keys(key)

    def _get_fallback_state(self) -> Dict[str, Any]:
        return {
            "grid": "Driver unavailable",
            "valid_actions": ['UP', 'DOWN', 'LEFT', 'RIGHT'],
            "steps": 0
        }

    def is_solvable(self) -> bool:
        return True

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()


class H5GameEnv(WebGameEnv):
    """
    H5 游戏专用适配器
    继承自 WebGameEnv，添加 H5 游戏特定的功能
    """

    def __init__(self, game_url: str = None, **kwargs):
        super().__init__(game_url, **kwargs)

    def get_state_description(self) -> Dict[str, Any]:
        state = super().get_state_description()
        state["type"] = "h5_game"
        return state


class CanvasGameEnv(WebGameEnv):
    """
    Canvas 游戏专用适配器
    专门用于测试基于 Canvas 的游戏
    """

    def __init__(self, game_url: str = None, **kwargs):
        super().__init__(game_url, **kwargs)

    def get_canvas_state(self) -> Optional[np.ndarray]:
        """获取 Canvas 内容"""
        if not self.is_connected:
            return None

        try:
            script = """
            const canvas = document.querySelector('canvas');
            if (canvas) {
                return canvas.toDataURL('image/png');
            }
            return null;
            """
            result = self.driver.execute_script(script)
            if result:
                import base64
                img_data = base64.b64decode(result.split(',')[1])
                return np.frombuffer(img_data, dtype=np.uint8)
        except Exception as e:
            print(f"获取 Canvas 状态失败: {e}")

        return None
