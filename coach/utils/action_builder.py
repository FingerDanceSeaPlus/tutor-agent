import chainlit as cl
from typing import List, Dict, Optional

class ActionBuilder:
    """
    动作按钮构建器
    用于统一构建和管理动作按钮
    """
    
    def __init__(self):
        pass
    
    def create_action(self, name: str, label: str, value: Optional[str] = None, payload: Optional[Dict] = None, icon: Optional[str] = None, tooltip: Optional[str] = None) -> cl.Action:
        """
        创建单个动作按钮
        """
        if value is None:
            value = name
        if payload is None:
            payload = {}
        
        return cl.Action(
            name=name,
            value=value,
            label=label,
            payload=payload,
            icon=icon,
            tooltip=tooltip
        )
    
    def create_actions(self, actions_config: List[Dict]) -> List[cl.Action]:
        """
        批量创建动作按钮
        """
        actions = []
        for config in actions_config:
            action = self.create_action(
                name=config.get("name"),
                label=config.get("label"),
                value=config.get("value"),
                payload=config.get("payload"),
                icon=config.get("icon"),
                tooltip=config.get("tooltip")
            )
            actions.append(action)
        return actions
    
    def create_problem_actions(self, has_problem: bool) -> List[cl.Action]:
        """
        创建题目相关的动作按钮
        """
        actions = []
        if not has_problem:
            actions.append(self.create_action(
                name="set_problem",
                label="设置题目",
                icon="file-text",
                tooltip="设置新的题目"
            ))
        else:
            actions.append(self.create_action(
                name="view_problem",
                label="查看题目",
                icon="eye",
                tooltip="查看当前题目"
            ))
        return actions
    
    def create_thinking_actions(self, has_thoughts: bool, hint_level: int) -> List[cl.Action]:
        """
        创建思路阶段的动作按钮
        """
        actions = []
        actions.append(self.create_action(
            name="submit_thoughts",
            label="提交思路",
            icon="edit",
            tooltip="提交你的解题思路"
        ))
        actions.append(self.create_action(
            name="need_hint",
            label=f"提示(L{hint_level})",
            icon="lightbulb",
            tooltip="获取解题提示"
        ))
        if has_thoughts:
            actions.append(self.create_action(
                name="continue",
                label="继续下一步",
                icon="arrow-right",
                tooltip="进入编码阶段"
            ))
        return actions
    
    def create_coding_actions(self, has_code: bool, hint_level: int) -> List[cl.Action]:
        """
        创建编码阶段的动作按钮
        """
        actions = []
        actions.append(self.create_action(
            name="submit_code",
            label="提交代码",
            icon="code",
            tooltip="提交你的代码实现"
        ))
        if has_code:
            actions.append(self.create_action(
                name="run_tests",
                label="运行测试",
                icon="play",
                tooltip="运行测试用例"
            ))
        actions.append(self.create_action(
            name="need_hint",
            label=f"提示(L{hint_level})",
            icon="lightbulb",
            tooltip="获取编码提示"
        ))
        return actions
    
    def create_testing_actions(self, has_code: bool) -> List[cl.Action]:
        """
        创建测试阶段的动作按钮
        """
        actions = []
        if not has_code:
            actions.append(self.create_action(
                name="submit_code",
                label="提交代码",
                icon="code",
                tooltip="提交你的代码实现"
            ))
        actions.append(self.create_action(
            name="run_tests",
            label="运行测试",
            icon="play",
            tooltip="运行测试用例"
        ))
        return actions
    
    def create_reflecting_actions(self, passed: bool, hint_level: int) -> List[cl.Action]:
        """
        创建复盘阶段的动作按钮
        """
        actions = []
        if passed:
            actions.append(self.create_action(
                name="variant",
                label="做变式题",
                icon="refresh-cw",
                tooltip="尝试类似的变式题"
            ))
            actions.append(self.create_action(
                name="next_problem",
                label="下一题",
                icon="chevron-right",
                tooltip="开始新的题目"
            ))
        else:
            actions.append(self.create_action(
                name="submit_code",
                label="提交修复代码",
                icon="code",
                tooltip="提交修复后的代码"
            ))
            actions.append(self.create_action(
                name="run_tests",
                label="再跑测试",
                icon="play",
                tooltip="再次运行测试用例"
            ))
            actions.append(self.create_action(
                name="need_hint",
                label=f"提示(L{hint_level})",
                icon="lightbulb",
                tooltip="获取修复提示"
            ))
        return actions

# 创建全局动作构建器实例
action_builder = ActionBuilder()
