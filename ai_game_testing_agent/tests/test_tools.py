"""测试Agent工具"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools import save_report, read_bug_list


def test_save_report():
    """测试保存报告"""
    report = {
        "report": {
            "session_id": "test_20240101",
            "env_type": "sokoban",
            "bugs": []
        },
        "filename": "test_report_1.json"
    }

    result = save_report.invoke(report)
    assert "Report saved" in result or "saved" in result.lower()


def test_read_bug_list_empty():
    """测试读取空的Bug列表"""
    result = read_bug_list.invoke("nonexistent.json")
    assert result == []


def test_save_report_with_bugs():
    """测试保存包含Bug的报告"""
    report = {
        "report": {
            "session_id": "test_20240101_2",
            "env_type": "sokoban",
            "bugs": [
                {
                    "type": "player_out_of_bounds",
                    "severity": "high",
                    "description": "测试Bug"
                }
            ]
        },
        "filename": "test_report_2.json"
    }

    result = save_report.invoke(report)
    assert "Report saved" in result or "saved" in result.lower()
