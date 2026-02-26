from coach.schemas import CoachState, Problem
import chainlit as cl
from typing import List, Dict, Any
class PhaseHandler:
    """
    按阶段处理用户交互
    """
    
    def __init__(self, state: CoachState):
        self.state = state
    
    def validate_state(self) -> bool:
        """
        验证状态的有效性
        """
        try:
            # 验证题目信息
            if not self.state.problem:
                return False
            
            # 验证阶段信息
            valid_phases = ["need_problem", "thinking", "coding", "testing", "reflecting"]
            if self.state.phase not in valid_phases:
                return False
            
            # 验证提示策略
            if not self.state.hint_policy:
                return False
            
            return True
        except Exception:
            return False
    
    def update_state(self, updates: Dict[str, Any]) -> CoachState:
        """
        更新状态并运行图处理
        """
        try:
            # 应用更新
            for key, value in updates.items():
                # 支持嵌套属性更新，如 "problem.title"
                if "." in key:
                    parts = key.split(".")
                    obj = getattr(self.state, parts[0])
                    setattr(obj, parts[1], value)
                else:
                    setattr(self.state, key, value)
            
            # 运行图处理
            out = GRAPH.invoke(self.state.model_dump())
            self.state = CoachState.model_validate(out)
            
            return self.state
        except Exception as e:
            print(f"Error updating state: {e}")
            return self.state
    
    def reset_state(self) -> CoachState:
        """
        重置状态到初始状态
        """
        self.state = init_state()
        return self.state
    
    def handle_error(self, error: Exception, context: str) -> CoachState:
        """
        处理错误并更新状态
        """
        error_message = f"{context}时发生错误: {str(error)}"
        print(error_message)
        import traceback
        traceback.print_exc()
        
        # 更新状态，添加错误信息
        self.state.ui_message = (
            "❌ 处理失败\n\n"
            f"错误信息：{str(error)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        return self.state
    
    async def handle_thinking_actions(self, action: cl.Action):
        """
        处理思路阶段的action
        """
        try:
            action_name = action.name
            
            if action_name == "submit_thoughts":
                return await self._handle_submit_thoughts()
            elif action_name == "need_hint":
                return await self._handle_need_hint()
            elif action_name == "continue":
                return await self._handle_continue()
            else:
                self.state.ui_message = f"未知的操作：{action_name}"
                return self.state
        except Exception as e:
            return self.handle_error(e, "处理思路阶段操作")
    
    async def handle_coding_actions(self, action: cl.Action):
        """
        处理编码阶段的action
        """
        try:
            action_name = action.name
            
            if action_name == "submit_code":
                return await self._handle_submit_code()
            elif action_name == "run_tests":
                return await self._handle_run_tests()
            elif action_name == "need_hint":
                return await self._handle_need_hint()
            else:
                self.state.ui_message = f"未知的操作：{action_name}"
                return self.state
        except Exception as e:
            return self.handle_error(e, "处理编码阶段操作")
    
    async def handle_testing_actions(self, action: cl.Action):
        """
        处理测试阶段的action
        """
        try:
            action_name = action.name
            
            if action_name == "submit_code":
                return await self._handle_submit_code()
            elif action_name == "run_tests":
                return await self._handle_run_tests()
            else:
                self.state.ui_message = f"未知的操作：{action_name}"
                return self.state
        except Exception as e:
            return self.handle_error(e, "处理测试阶段操作")
    
    async def handle_reflecting_actions(self, action: cl.Action):
        """
        处理复盘阶段的action
        """
        try:
            action_name = action.name
            
            if action_name == "variant":
                return await self._handle_variant()
            elif action_name == "next_problem":
                return await self._handle_next_problem()
            elif action_name == "submit_code":
                return await self._handle_submit_code()
            elif action_name == "run_tests":
                return await self._handle_run_tests()
            elif action_name == "need_hint":
                return await self._handle_need_hint()
            else:
                self.state.ui_message = f"未知的操作：{action_name}"
                return self.state
        except Exception as e:
            return self.handle_error(e, "处理复盘阶段操作")
    
    async def handle_need_problem_actions(self, action: cl.Action):
        """
        处理需要题目的action
        """
        try:
            action_name = action.name
            
            if action_name == "set_problem":
                return await self._handle_set_problem()
            else:
                self.state.ui_message = f"未知的操作：{action_name}"
                return self.state
        except Exception as e:
            return self.handle_error(e, "处理设置题目操作")
    
    async def _handle_set_problem(self) -> CoachState:
        """
        处理设置题目
        """
        try:
            res = await cl.AskUserMessage(
                content="请黏贴题目原文（包含样例 Input/Output）。",
                timeout=60000
            ).send()
            
            if res:
                raw = res["output"]
                cases = parse_examples_from_text(raw)
                title = summarize_title(raw)
                constraints = extract_constraints(raw)

                # 暂时保存解析结果，进入检查阶段
                self.state.problem.raw_text = raw
                self.state.problem.title = title
                self.state.problem.statement = raw[:1200]  # MVP：展示截断；完整保存在 raw_text
                self.state.problem.constraints = constraints
                self.state.problem.testcases = cases
                self.state.problem.examples = "\n---\n".join(
                        [f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in cases[:5]]
                    )
                
                # 进入检查和完善阶段
                return await self._handle_review_problem()
            else:
                self.state.ui_message = "你取消了设置题目。"
                return self.state
        except Exception as e:
            return self.handle_error(e, "设置题目")
    
    async def _handle_review_problem(self) -> CoachState:
        """
        处理用户检查和完善题目内容
        """
        try:
            # 显示解析结果，让用户检查
            content = f"### 题目解析结果\n\n"
            content += f"**标题**：{self.state.problem.title}\n\n"
            content += f"**描述**：{self.state.problem.statement}\n\n"
            content += f"**约束条件**：{self.state.problem.constraints or '无'}\n\n"
            content += f"**测试用例数**：{len(self.state.problem.testcases)}\n\n"
            content += f"**样例**：\n{self.state.problem.examples or '无'}\n\n"
            content += "请检查以上信息是否正确，如需修改请重新设置题目。"
            
            # 提供确认和重新设置的选项
            res = await cl.AskUserMessage(
                content=content,
                timeout=60000,
                actions=[
                    cl.Action(name="confirm_problem", value="confirm_problem", label="确认题目", payload={}),
                    cl.Action(name="reset_problem", value="reset_problem", label="重新设置", payload={})
                ]
            ).send()
            
            if res and res["action"] and res["action"]["name"] == "confirm_problem":
                # 确认题目，进入思路阶段
                self.state.phase = "thinking"
                out = GRAPH.invoke(self.state.model_dump())
                self.state = CoachState.model_validate(out)
                return self.state
            elif res and res["action"] and res["action"]["name"] == "reset_problem":
                # 重新设置题目
                return await self._handle_set_problem()
            else:
                self.state.ui_message = "你取消了题目检查。"
                return self.state
        except Exception as e:
            return self.handle_error(e, "检查题目")
    
    async def _handle_submit_thoughts(self) -> CoachState:
        """
        处理提交思路
        """
        try:
            res = await cl.AskUserMessage(
                content="请输入你的解题思路：\n\n" +
                "1) 你对题意的复述\n" +
                "2) 关键约束/边界条件\n" +
                "3) 你打算使用的算法\n" +
                "4) 不变量分析\n" +
                "5) 时间和空间复杂度分析",
                timeout=60000
            ).send()
            
            if res:
                # 使用update_state方法更新状态
                self.update_state({"user_attempt.thoughts": res["output"]})
            else:
                self.state.ui_message = "你取消了提交思路。"
            
            return self.state
        except Exception as e:
            return self.handle_error(e, "提交思路")
    
    async def _handle_submit_code(self) -> CoachState:
        """
        处理提交代码
        """
        try:
            res = await cl.AskUserMessage(
                content="请输入你的代码实现：\n\n" +
                "请确保：\n" +
                "- 定义 `solve(inp: str) -> str` 函数\n" +
                "- 正确处理输入输出格式\n" +
                "- 考虑所有边界条件",
                timeout=60000
            ).send()
            
            if res:
                # 使用update_state方法更新状态
                self.update_state({"user_attempt.code": res["output"]})
            else:
                self.state.ui_message = "你取消了提交代码。"
            
            return self.state
        except Exception as e:
            return self.handle_error(e, "提交代码")
    
    async def _handle_run_tests(self) -> CoachState:
        """
        处理运行测试
        """
        try:
            # 检查是否有代码
            if not self.state.user_attempt.code:
                self.state.ui_message = "请先提交你的代码实现。"
                return self.state
            
            # 使用update_state方法更新状态
            self.update_state({"phase": "testing"})
            
            return self.state
        except Exception as e:
            return self.handle_error(e, "运行测试")
    
    async def _handle_need_hint(self) -> CoachState:
        """
        处理需要提示
        """
        try:
            # 增加提示等级
            new_level = min(self.state.hint_policy.max_level, self.state.hint_policy.level + 1)
            new_hint_count = self.state.hint_policy.hint_count + 1
            
            # 更新提示策略
            self.state.hint_policy.level = new_level
            self.state.hint_policy.hint_count = new_hint_count
            
            # 根据当前阶段提供相应的提示
            if self.state.phase == "thinking":
                # 思路阶段的提示
                self.state.ui_message = (
                    f"### 提示 (等级 {new_level})\n\n"
                    "**思路提示**：\n"
                    "1) 尝试将问题分解为更小的子问题\n"
                    "2) 考虑常见的算法模式，如贪心、动态规划、分治等\n"
                    "3) 分析问题的边界条件和特殊情况\n"
                    "4) 思考算法的时间和空间复杂度"
                )
            elif self.state.phase == "coding":
                # 编码阶段的提示
                self.state.ui_message = (
                    f"### 提示 (等级 {new_level})\n\n"
                    "**代码提示**：\n"
                    "1) 确保函数签名正确：`def solve(inp: str) -> str`\n"
                    "2) 注意输入输出格式的处理\n"
                    "3) 检查边界条件的处理\n"
                    "4) 确保代码逻辑与思路一致"
                )
            else:
                # 通用提示
                self.state.ui_message = (
                    f"### 提示 (等级 {new_level})\n\n"
                    "如果你遇到困难，可以：\n"
                    "1) 重新审视题目要求\n"
                    "2) 检查你的思路是否完整\n"
                    "3) 考虑常见的错误点\n"
                    "4) 尝试简化问题，从小规模示例入手"
                )
            
            return self.state
        except Exception as e:
            return self.handle_error(e, "获取提示")
    
    async def _handle_continue(self) -> CoachState:
        """
        处理继续下一步
        """
        try:
            # 直接进入编码阶段
            self.update_state({"phase": "coding"})
            return self.state
        except Exception as e:
            return self.handle_error(e, "继续下一步")
    
    async def _handle_variant(self) -> CoachState:
        """
        处理做变式题
        """
        try:
            self.state.ui_message = "变式题功能正在开发中，敬请期待！"
            return self.state
        except Exception as e:
            return self.handle_error(e, "获取变式题")
    
    async def _handle_next_problem(self) -> CoachState:
        """
        处理下一题
        """
        try:
            # 重置状态，准备新题目
            self.state = init_state()
            self.state.ui_message = "请粘贴新的题目文本。"
            return self.state
        except Exception as e:
            return self.handle_error(e, "下一题")