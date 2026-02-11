# coach/problem_parser.py
from __future__ import annotations
import re
from typing import List, Dict, Tuple

EX_SPLIT_RE = re.compile(r"\n-{3,}\n")

def _clean(s: str) -> str:
    return s.strip("\n\r\t ")

def parse_examples_from_text(problem_text: str) -> List[Dict[str, str]]:
    """
    从题干中抽取样例，支持常见格式：
    - Input: ... Output: ...
    - 输入：... 输出：...
    - INPUT: ... OUTPUT: ...
    多组样例用 --- 分隔（可选），否则用多次匹配收集。
    """
    text = problem_text

    # 统一中英标记
    patterns = [
        (r"(?:Input|INPUT|输入)\s*[:：]\s*(?P<input>.*?)(?:Output|OUTPUT|输出)\s*[:：]\s*(?P<output>.*?)(?=\n(?:Input|INPUT|输入)\s*[:：]|\Z)", re.S),
    ]

    cases: List[Dict[str, str]] = []
    for pat, flags in patterns:
        for m in re.finditer(pat, text, flags):
            inp = _clean(m.group("input"))
            out = _clean(m.group("output"))
            if inp and out:
                cases.append({"input": inp + "\n", "expected": out + "\n"})

    # 如果没匹配到，尝试用 --- 块 + INPUT/OUTPUT 标记
    if not cases:
        blocks = EX_SPLIT_RE.split(text)
        for b in blocks:
            if re.search(r"(?:INPUT|Input|输入)\s*[:：]", b) and re.search(r"(?:OUTPUT|Output|输出)\s*[:：]", b):
                inp = re.split(r"(?:OUTPUT|Output|输出)\s*[:：]", b, maxsplit=1, flags=re.S)[0]
                inp = re.split(r"(?:INPUT|Input|输入)\s*[:：]", inp, maxsplit=1, flags=re.S)[-1]
                out = re.split(r"(?:OUTPUT|Output|输出)\s*[:：]", b, maxsplit=1, flags=re.S)[-1]
                inp, out = _clean(inp), _clean(out)
                if inp and out:
                    cases.append({"input": inp + "\n", "expected": out + "\n"})

    # 去重（按 input+expected）
    uniq = []
    seen = set()
    for c in cases:
        k = (c["input"], c["expected"])
        if k not in seen:
            uniq.append(c)
            seen.add(k)
    return uniq

def extract_constraints(problem_text: str) -> str:
    """
    粗抽取 constraints 段（可后续用 LLM/规则增强）
    """
    # 常见关键字：Constraints / 约束 / 数据范围
    m = re.search(r"(Constraints|约束|数据范围)\s*[:：]\s*(.*)", problem_text, re.I)
    return m.group(2).strip() if m else ""

def summarize_title(problem_text: str) -> str:
    """
    尝试从第一行抽题目标题（MVP）
    """
    first = problem_text.strip().splitlines()[0] if problem_text.strip() else "Untitled"
    return first[:80]
