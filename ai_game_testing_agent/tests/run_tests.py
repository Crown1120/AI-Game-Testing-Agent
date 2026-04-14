"""AI游戏测试系统单元测试"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 导入所有测试模块
from tests import test_config
from tests import test_sokoban
from tests import test_tools


def run_all_tests():
    """运行所有测试"""
    tests = [
        ("Config Tests", test_config),
        ("SokobanEnv Tests", test_sokoban),
        ("Agent Tools Tests", test_tools),
    ]

    passed = 0
    failed = 0

    for name, module in tests:
        print(f"\n{'='*50}")
        print(f"运行: {name}")
        print('='*50)

        for func_name in dir(module):
            if func_name.startswith('test_'):
                func = getattr(module, func_name)
                try:
                    func()
                    print(f"✓ {func_name}")
                    passed += 1
                except Exception as e:
                    print(f"✗ {func_name}: {e}")
                    failed += 1

    print(f"\n{'='*50}")
    print(f"总计: {passed} 通过, {failed} 失败")
    print('='*50)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
