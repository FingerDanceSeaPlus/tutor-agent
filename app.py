# coach/app.py
from __future__ import annotations
import chainlit as cl
from coach.schemas import CoachState, Problem
from coach.graph import build_graph
from coach.problem_parser import *
from typing import List, Dict, Any

GRAPH = build_graph()

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

async def route_action(state: CoachState, action: cl.Action) -> CoachState:
    """
    根据当前阶段和action类型路由到对应处理函数
    """
    try:
        phase = state.phase
        
        handler = PhaseHandler(state)
        
        # 验证状态
        if not handler.validate_state():
            state.ui_message = "状态验证失败，请重新设置题目。"
            return state
        
        if phase == "thinking":
            return await handler.handle_thinking_actions(action)
        elif phase == "coding":
            return await handler.handle_coding_actions(action)
        elif phase == "testing":
            return await handler.handle_testing_actions(action)
        elif phase == "reflecting":
            return await handler.handle_reflecting_actions(action)
        else:
            # 处理未识别的阶段
            state.ui_message = f"未知的阶段：{phase}"
            return state
    except Exception as e:
        print(f"Error in route_action: {e}")
        import traceback
        traceback.print_exc()
        
        # 错误处理
        state.ui_message = (
            "❌ 路由处理失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        return state

def init_state() -> CoachState:
    # 初始无题：提示用户先设置
    p = Problem(
        source="custom",
        id="custom-001",
        title="(未设置题目)",
        statement="请先粘贴题目原文。",
        raw_text="",
        constraints="",
        examples="",
        testcases=[]
    )
    return CoachState(problem=p)

def has_problem(state: CoachState) -> bool:
    # 你如果升级了 raw_text/testcases，这里也可加判断
    title = (state.problem.title or "").strip()
    return title not in {"", "(未设置题目)"} and (state.problem.statement or "").strip() != ""

def has_thoughts(state: CoachState) -> bool:
    return bool((state.user_attempt.thoughts or "").strip())

def has_code(state: CoachState) -> bool:
    return bool((state.user_attempt.code or "").strip())

def passed(state: CoachState) -> bool:
    try:
        return bool(state.evaluation.passed)
    except Exception:
        return False
def stage_actions(state: CoachState) -> List[cl.Action]:
    """
    核心：根据当前“教学阶段”返回不同按钮集合。
    使用 phase 驱动路由，根据当前教学阶段显示不同的按钮。
    """
    actions: List[cl.Action] = []

    # 0) 题目尚未设置：强制只显示“设置题目”（避免误操作）
    if not has_problem(state):
        actions.append(cl.Action(name="set_problem", value="set_problem", label="设置题目"))
        return actions

    # 通用按钮（但不要太多）
    actions.append(cl.Action(name="view_problem", value="view_problem", label="查看题目"))

    # 根据当前阶段显示不同按钮
    phase = state.phase

    # 1) 思路阶段：强调“提交思路”
    if phase == "thinking":
        actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        # 如果已有思路，可直接推进
        if has_thoughts(state):
            actions.append(cl.Action(name="continue", value="continue", label="继续下一步"))
        return actions

    # 2) 编码阶段：强调“提交代码 / 运行测试”
    if phase == "coding":
        actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
        if has_code(state):
            actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        return actions

    # 3) 测试阶段：只给“运行测试”（以及必要时提交代码）
    if phase == "testing":
        if not has_code(state):
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
        actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
        return actions

    # 4) 复盘阶段：通过/未通过给不同按钮
    if phase == "reflecting":
        if passed(state):
            actions.append(cl.Action(name="variant", value="variant", label="做变式题"))
            actions.append(cl.Action(name="next_problem", value="next_problem", label="下一题"))
        else:
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交修复代码"))
            actions.append(cl.Action(name="run_tests", value="run_tests", label="再跑测试"))
            actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        return actions

    # 5) 兜底：给最小集合
    actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"))
    actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
    actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
    actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
    return actions

async def render(state: CoachState, actions: List):
    await cl.Message(content=state.ui_message,actions=actions).send()

async def run_graph_once(state: CoachState) -> CoachState:
    """
    运行图处理一次，处理异常情况
    """
    try:
        # LangGraph 支持 dict；这里用 model_dump / model_validate 来回转换更稳
        out = GRAPH.invoke(state.model_dump(),config={
            "recursion_limit": 25,
            "debug": True
        })
        return CoachState.model_validate(out)
    except Exception as e:
        print(f"Error running graph: {e}")
        import traceback
        traceback.print_exc()
        # 错误处理：保持状态不变，添加错误信息
        state.ui_message = (
            "❌ 处理失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        return state




@cl.on_chat_start
async def on_start():
    state = init_state()
    state.ui_message=(
        "你好，我是智能编程学习助手。\n\n"
        "请选择合适的功能"
    )
    cl.user_session.set("state", state)
        
    # 动作按钮
    actions=[
        cl.Action(name="coach",payload={"value": "example_value"},icon="graduation-cap",label="指导性刷题",tooltip="在agent指导下按一定流程进行学习"),
        cl.Action(name="search",payload={"value": "example_value"},icon="search",label="知识库检索",tooltip="在知识库中针对用户输入进行检索")
    ]
    await render(state,actions)
   

@cl.action_callback("coach")
async def on_coach(action: cl.Action):
    """
    处理指导性刷题
    """
    state: CoachState = cl.user_session.get("state")
    
    # 直接调用设置题目的回调
    await on_set_problem(action)


@cl.action_callback("search")
async def on_search(action: cl.Action):
    """
    处理知识库检索
    """
    state: CoachState = cl.user_session.get("state")
    
    res = await cl.AskUserMessage(
        content="请输入你想检索的问题：",
        timeout=60000
    ).send()
    
    if res:
        query = res["output"]
        state.ui_message = f"知识库检索功能正在开发中，你的查询：{query}"
    else:
        state.ui_message = "你取消了知识库检索。"
    
    cl.user_session.set("state", state)
    await cl.Message(
        content=state.ui_message,
        actions=stage_actions(state)
    ).send()


@cl.action_callback("set_problem")
async def on_set_problem(action: cl.Action):
    """
    处理设置题目
    """
    state: CoachState = cl.user_session.get("state")
    
    res = await cl.AskUserMessage(
        content="请黏贴题目原文（包含样例 Input/Output）。",
        timeout=60000
    ).send()
    
    if res:
        raw = res["output"]
        cases = parse_examples_from_text(raw)
        title = summarize_title(raw)
        constraints = extract_constraints(raw)

        state.problem.raw_text = raw
        state.problem.title = title
        state.problem.statement = raw[:1200]  # MVP：展示截断；完整保存在 raw_text
        state.problem.constraints = constraints
        state.problem.testcases = cases
        state.problem.examples = "\n---\n".join(
                [f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in cases[:5]]
            )
        # 设置题目后，进入思路阶段
        state.phase = "thinking"

        out = GRAPH.invoke(state.model_dump())
        state = CoachState.model_validate(out)

        cl.user_session.set("state", state)
        await cl.Message(
                content=(
                    f"✅ 已设置题目：**{state.problem.title}**\n"
                    f"- 抽取到测试用例数：{len(state.problem.testcases)}\n\n"
                    + state.ui_message
                ),
                actions=stage_actions(state)
        ).send()
    else:
        await cl.Message(content="你取消了设置题目。").send()


@cl.action_callback("view_problem")
async def on_view_problem(action: cl.Action):
    """
    处理查看题目
    """
    state: CoachState = cl.user_session.get("state")
    
    content = f"### {state.problem.title}\n\n"
    content += f"**题目描述**：\n{state.problem.statement}\n\n"
    content += f"**约束条件**：\n{state.problem.constraints or '无'}\n\n"
    content += f"**样例**：\n{state.problem.examples or '无'}"
    
    await cl.Message(content=content).send()


@cl.action_callback("submit_thoughts")
@cl.action_callback("submit_code")
@cl.action_callback("run_tests")
@cl.action_callback("need_hint")
@cl.action_callback("continue")
@cl.action_callback("variant")
@cl.action_callback("next_problem")
async def on_action(action: cl.Action):
    """
    统一处理action回调
    """
    state: CoachState = cl.user_session.get("state")
    
    try:
        # 路由到对应处理函数
        updated_state = await route_action(state, action)
        
        # 更新会话状态
        cl.user_session.set("state", updated_state)
        
        # 发送响应
        await cl.Message(
            content=updated_state.ui_message,
            actions=stage_actions(updated_state)
        ).send()
    except Exception as e:
        print(f"Error handling action: {e}")
        import traceback
        traceback.print_exc()
        
        # 错误处理
        state.ui_message = (
            "❌ 处理失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        cl.user_session.set("state", state)
        await cl.Message(
            content=state.ui_message,
            actions=stage_actions(state)
        ).send()
