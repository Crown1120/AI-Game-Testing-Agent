"""
Windows 自带游戏测试报告

测试日期: 2026-04-10
测试系统: Windows 11 Home China

=== 测试结果 ===

1. Microsoft Solitaire Collection (推箱子/纸牌游戏)
   - 状态: ✓ 完全支持
   - 路径: C:\Program Files\WindowsApps\Microsoft.MicrosoftSolitaireCollection_4.25.4020.0_x64__8wekyb3d8bbwe\Solitaire.exe
   - 版本: 4.25.4020.0
   - 测试结果:
     * 游戏启动: 成功
     * 状态获取: 成功 (屏幕尺寸: 2560x1600)
     * 动作执行: 成功
     * 屏幕截图: 成功 (分辨率: 2560x1600x3)

2. Microsoft Minesweeper
   - 状态: ✗ 未安装
   - 说明: 需要从 Microsoft Store 安装

3. 经典游戏 (sol.exe, freecell.exe 等)
   - 状态: ✗ 不存在
   - 说明: Windows 11 已移除经典游戏文件

=== 支持的游戏列表 ===

| 游戏名称 | 状态 | 说明 |
|----------|------|------|
| Microsoft Solitaire Collection | ✓ 支持 | 包含纸牌、推箱子等 |
| Microsoft Minesweeper | ✗ 需安装 | 可从 Microsoft Store 安装 |
| Xbox Game Bar | ✓ 支持 | 游戏录制功能 |

=== 使用方法 ===

```python
from game_env import PCGameEnv

# 测试 Solitaire
env = PCGameEnv(
    game_path=r'C:\Program Files\WindowsApps\Microsoft.MicrosoftSolitaireCollection_4.25.4020.0_x64__8wekyb3d8bbwe\Solitaire.exe',
    game_name='Microsoft Solitaire Collection',
    wait_for_start=3
)

# 重置游戏
state = env.reset()

# 获取屏幕信息
print(f"屏幕尺寸: {state['screen_size']}")

# 执行动作
new_state, reward, done, info = env.step('JUMP')

# 截图
img = env.render()
print(f"截图形状: {img.shape}")

# 关闭游戏
env.close()
```

=== 注意事项 ===

1. Windows 11 的 Microsoft Solitaire Collection 是 UWP 应用
2. 需要先启动游戏才能进行控制
3. pyautogui 需要管理员权限才能控制某些应用
4. 如果遇到权限问题，可以尝试以管理员身份运行 Python

=== 推荐测试流程 ===

1. 确保 Microsoft Solitaire Collection 已安装
2. 运行测试脚本
3. 观察游戏是否正常启动和控制
4. 查看截图是否正确捕获游戏画面
