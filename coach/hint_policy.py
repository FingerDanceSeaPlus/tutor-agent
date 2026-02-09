# coach/hint_policy.py
from __future__ import annotations
from dataclasses import dataclass

@dataclass
class HintPolicy:
    max_level: int = 5
    final_answer_level: int = 5

    def bump(self, level: int) -> int:
        if level < self.max_level:
            return level + 1
        return level

    def can_give_final(self, level: int) -> bool:
        """
        判断是否能给出最终结果
        
        :param self: 说明
        :param level: 说明
        :type level: int
        :return: 说明
        :rtype: bool
        """
        return level >= self.final_answer_level

def format_hint_header(level: int) -> str:
    return f"### 提示等级 L{level}\n"

def hint_rules(level: int) -> str:
    # 作为“规范”，你后续可以写进系统提示或节点约束
    rules = {
        0: "只做题意澄清与关键约束抽取；不提供算法方向。",
        1: "给一句关键观察/转化；不提供完整算法流程。",
        2: "给算法类别与适用理由；不提供伪码。",
        3: "给伪码骨架/不变量/边界；不给完整可复制代码。",
        4: "给代码框架（函数签名+关键循环）；不给全部细节。",
        5: "可给完整参考解 + 逐行解释 + 变式训练。",
    }
    return f"- 规则：{rules.get(level, rules[0])}\n"
