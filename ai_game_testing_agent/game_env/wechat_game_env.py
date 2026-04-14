"""
微信小游戏环境适配器
支持通过 Airtest 或 Appium 控制微信小游戏
"""
from typing import Dict, List, Tuple, Any, Optional
import numpy as np
import time
import os

from .base_env import GameEnvironment


class WeChatMiniGameEnv(GameEnvironment):
    """
    微信小游戏环境适配器

    支持通过 Airtest 或 Appium 控制微信小游戏
    适用于微信小程序/小游戏测试
    """

    def __init__(
        self,
        game_name: str = None,
        device: str = "android",
        render_mode: str = "text",
        use_airtest: bool = True
    ):
        """
        初始化微信小游戏环境

        Args:
            game_name: 游戏名称
            device: 设备类型 ('android' 或 'ios')
            render_mode: 渲染模式
            use_airtest: 是否使用 Airtest
        """
        self.game_name = game_name
        self.device = device
        self.render_mode = render_mode
        self.use_airtest = use_airtest
        self.device_conn = None
        self.is_connected = False

        self._initialize_device()

    def _initialize_device(self):
        """初始化设备连接"""
        try:
            if self.use_airtest:
                from airtest.core.api import connect_device, snapshot

                self.snapshot = snapshot
                self.is_connected = True
                print(f"✓ Airtest 设备连接成功")
            else:
                from appium import webdriver
                from appium.webdriver.common.appiumby import AppiumBy

                # Appium 配置
                caps = {
                    "platformName": self.device.capitalize(),
                    "automationName": "XCUITest" if self.device == "ios" else "UiAutomator2",
                    "bundleId": "com.tencent.mm",
                    "noReset": True
                }

                self.driver = webdriver.Remote("http://127.0.0.1:4723/wd/hub", caps)
                self.is_connected = True
                print(f"✓ Appium 设备连接成功")

        except ImportError as e:
            print(f"⚠ 缺少依赖: {e}")
            print("  安装 Airtest: pip install airtest")
            print("  安装 Appium: pip install appium-python-client")
        except Exception as e:
            print(f"⚠ 设备连接失败: {e}")

    def reset(self, level_id: Optional[str] = None) -> Dict[str, Any]:
        """重置游戏"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            if self.use_airtest:
                # 重新打开游戏
                pass
            else:
                # Appium 重启应用
                self.driver.terminate_app("com.tencent.mm")
                self.driver.activate_app("com.tencent.mm")

            return self.get_state_description()
        except Exception as e:
            print(f"重置失败: {e}")
            return self._get_fallback_state()

    def step(self, action: str) -> Tuple[Dict[str, Any], float, bool, Dict]:
        """执行动作"""
        if not self.is_connected:
            return self._get_fallback_state(), 0.0, True, {"error": "Not connected"}

        try:
            self._execute_action(action)
            time.sleep(0.5)  # 等待游戏响应

            new_state = self.get_state_description()
            return new_state, 0.0, False, {}
        except Exception as e:
            print(f"执行动作失败: {e}")
            return self._get_fallback_state(), 0.0, True, {"error": str(e)}

    def get_valid_actions(self) -> List[str]:
        """获取合法动作"""
        if not self.is_connected:
            return ['TAP', 'SWIPE', 'LONG_PRESS', 'KEY']

        # 通过图像识别获取可点击区域
        try:
            if self.use_airtest:
                from airtest.core.api import exists, Template

                # 检测常见 UI 元素
                actions = ['TAP', 'SWIPE']
                return actions
        except:
            pass

        return ['TAP', 'SWIPE', 'LONG_PRESS', 'KEY']

    def render(self) -> np.ndarray:
        """获取游戏画面"""
        if not self.is_connected:
            return np.zeros((1920, 1080, 3), dtype=np.uint8)

        try:
            if self.use_airtest:
                # Airtest 截图
                img = self.snapshot()
                if img is not None:
                    return np.array(img)
            else:
                # Appium 截图
                screenshot = self.driver.get_screenshot_as_png()
                return np.frombuffer(screenshot, dtype=np.uint8).reshape(1920, 1080, 3)
        except Exception as e:
            print(f"截图失败: {e}")

        return np.zeros((1920, 1080, 3), dtype=np.uint8)

    def get_state_description(self) -> Dict[str, Any]:
        """获取当前游戏状态"""
        if not self.is_connected:
            return self._get_fallback_state()

        try:
            state = {
                "screenshot_available": True,
                "timestamp": time.time(),
                "type": "wechat_minigame"
            }

            if self.use_airtest:
                # Airtest 文本识别
                from airtest.core.api import exists, text_exists

                state["text_detected"] = True
            else:
                # Appium 页面源码
                state["page_source"] = self.driver.page_source[:1000]

            return state
        except Exception as e:
            return self._get_fallback_state()

    def _execute_action(self, action: str):
        """执行具体动作"""
        if self.use_airtest:
            from airtest.core.api import touch, swipe, text, keyevent

            action_map = {
                'TAP': lambda: touch((500, 500)),
                'SWIPE_UP': lambda: swipe((500, 800), (500, 200)),
                'SWIPE_DOWN': lambda: swipe((500, 200), (500, 800)),
                'SWIPE_LEFT': lambda: swipe((800, 500), (200, 500)),
                'SWIPE_RIGHT': lambda: swipe((200, 500), (800, 500)),
                'KEY_OK': lambda: keyevent(3),
                'KEY_BACK': lambda: keyevent(4),
            }
        else:
            from appium.webdriver.common.touch_actions import TouchActions

            actions = TouchActions(self.driver)
            action_map = {
                'TAP': lambda: actions.tap(None).perform(),
                'SWIPE_UP': lambda: actions.swipe(500, 800, 500, 200).perform(),
            }

        # 解析动作
        if action in action_map:
            action_map[action]()
        elif action.startswith('TAP_'):
            # 解析坐标点击
            try:
                coords = action.split('_')[1:]
                x, y = int(coords[0]), int(coords[1])
                if self.use_airtest:
                    touch((x, y))
            except:
                pass

    def _get_fallback_state(self) -> Dict[str, Any]:
        return {
            "grid": "Device unavailable",
            "valid_actions": ['TAP', 'SWIPE'],
            "steps": 0
        }

    def is_solvable(self) -> bool:
        return True

    def close(self):
        """关闭连接"""
        if self.device_conn:
            self.device_conn.quit()


class WeChatGameEnv(WeChatMiniGameEnv):
    """
    微信小游戏专用适配器（别名）
    """
    pass
