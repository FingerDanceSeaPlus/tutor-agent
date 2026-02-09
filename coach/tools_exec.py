# coach/tools_exec.py
from __future__ import annotations
import textwrap
import traceback
from typing import Dict, Any, List

def run_solution(user_code: str, inp: str) -> Dict[str, Any]:
    """
    约定：用户代码必须定义 solve(inp: str) -> str
    """
    g = {}
    try:
        exec(user_code, g, g)
        if "solve" not in g:
            return {"ok": False, "error": "未找到 solve(inp: str) -> str 函数。"}
        out = g["solve"](inp)
        if not isinstance(out, str):
            out = str(out)
        return {"ok": True, "output": out}
    except Exception:
        return {"ok": False, "error": traceback.format_exc()}

def run_tests(user_code: str, testcases: List[Dict[str, str]]) -> Dict[str, Any]:
    failing = []
    for i, tc in enumerate(testcases, 1):
        r = run_solution(user_code, tc["input"])
        if not r["ok"]:
            failing.append({"case": i, "input": tc["input"], "expected": tc["expected"], "error": r["error"]})
            continue
        got = (r["output"] or "").strip()
        exp = (tc["expected"] or "").strip()
        if got != exp:
            failing.append({"case": i, "input": tc["input"], "expected": exp, "got": got})
    return {"passed": len(failing) == 0, "failing": failing}

def generate_edge_cases() -> List[Dict[str, str]]:
    # MVP：先返回空；后续按题型生成
    return []

def default_plan_steps() -> List[str]:
    return [
        "复述题意（你用自己的话说一遍）",
        "列出关键约束与边界（n 范围/是否负数/是否重复/空输入等）",
        "写出建模与不变量（例如窗口含义/哈希含义/状态定义）",
        "确定算法与复杂度（为什么是它，时间/空间）",
        "写 3~8 行伪码",
        "实现并跑样例/边界测试",
        "复盘：错因卡 + 解题模板 + 变式",
    ]
