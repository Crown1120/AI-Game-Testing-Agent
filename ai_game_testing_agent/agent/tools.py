import json
import os
from typing import Dict, Any, List
from langchain_core.tools import tool

@tool
def save_report(report: Dict[str, Any], filename: str = "test_report.json") -> str:
    """将测试报告保存为JSON文件

    Args:
        report: 测试报告字典
        filename: 文件名，默认为 test_report.json
    """
    os.makedirs("data/reports", exist_ok=True)
    path = os.path.join("data/reports", filename)
    with open(path, 'w') as f:
        json.dump(report, f, indent=2)
    return f"Report saved to {path}"

@tool
def read_bug_list(filename: str) -> List[Dict[str, Any]]:
    """读取历史Bug列表

    Args:
        filename: 报告文件名
    """
    path = os.path.join("data/reports", filename)
    if not os.path.exists(path):
        return []
    with open(path, 'r') as f:
        data = json.load(f)
    return data.get("bugs", [])
