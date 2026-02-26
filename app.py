# coach/app.py
from __future__ import annotations
import chainlit as cl
from coach.schemas import CoachState
from coach.handlers import action_handler
from coach.services import StateService, ProblemService
from typing import List

# 初始化服务
state_service = StateService()
problem_service = ProblemService()


def stage_actions(state: CoachState) -> List[cl.Action]:
    """
    核心：根据当前“教学阶段”返回不同按钮集合。
    使用 phase 驱动路由，根据当前教学阶段显示不同的按钮。
    """
    actions: List[cl.Action] = []

    # 0) 题目尚未设置：强制只显示“设置题目”（避免误操作）
    if not state_service.has_problem(state):
        actions.append(cl.Action(name="set_problem", value="set_problem", label="设置题目", payload={}))
        return actions

    # 通用按钮（但不要太多）
    actions.append(cl.Action(name="view_problem", value="view_problem", label="查看题目", payload={}))

    # 根据当前阶段显示不同按钮
    phase = state.phase

    # 0) 题目检查阶段：显示确认和重新设置按钮
    # 检查是否处于题目设置后的检查阶段
    if phase == "need_problem" and state_service.has_problem(state):
        actions.append(cl.Action(name="confirm_problem", value="confirm_problem", label="确认题目", payload={}))
        actions.append(cl.Action(name="reset_problem", value="reset_problem", label="重新设置", payload={}))
        return actions

    # 1) 需要题目阶段：只显示“设置题目”
    if phase == "need_problem":
        actions.append(cl.Action(name="set_problem", value="set_problem", label="设置题目", payload={}))
        return actions

    # 2) 思路阶段：强调“提交思路”
    if phase == "thinking":
        actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路", payload={}))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})", payload={}))
        # 如果已有思路，可直接推进
        if state_service.has_thoughts(state):
            actions.append(cl.Action(name="continue", value="continue", label="继续下一步", payload={}))
        return actions

    # 3) 编码阶段：强调“提交代码 / 运行测试”
    if phase == "coding":
        actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码", payload={}))
        if state_service.has_code(state):
            actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试", payload={}))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})", payload={}))
        return actions

    # 4) 测试阶段：只给“运行测试”（以及必要时提交代码）
    if phase == "testing":
        if not state_service.has_code(state):
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码", payload={}))
        actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试", payload={}))
        return actions

    # 5) 复盘阶段：通过/未通过给不同按钮
    if phase == "reflecting":
        if state_service.passed(state):
            actions.append(cl.Action(name="variant", value="variant", label="做变式题", payload={}))
            actions.append(cl.Action(name="next_problem", value="next_problem", label="下一题", payload={}))
        else:
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交修复代码", payload={}))
            actions.append(cl.Action(name="run_tests", value="run_tests", label="再跑测试", payload={}))
            actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})", payload={}))
        return actions

    # 6) 兜底：给最小集合
    actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路", payload={}))
    actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码", payload={}))
    actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试", payload={}))
    actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})", payload={}))
    return actions

async def render(state: CoachState, actions: List):
    await cl.Message(content=state.ui_message,actions=actions).send()


@cl.on_chat_start
async def on_start():
    state = state_service.init_state()
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
    actions=[
        cl.Action(name="set_problem", value="set_problem", label="设置题目", payload={})
    ]
    state.ui_message=(
        "请先设置题目"
    )
    
    # 直接调用设置题目的回调
    await render(state,actions)


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
    
    try:
        # 使用动作处理器处理设置题目
        updated_state = await action_handler.route_action(state, action)
        
        # 更新会话状态
        cl.user_session.set("state", updated_state)
        
        # 发送响应
        await cl.Message(
            content=updated_state.ui_message,
            actions=stage_actions(updated_state)
        ).send()
    except Exception as e:
        print(f"Error in on_set_problem: {e}")
        import traceback
        traceback.print_exc()
        
        # 错误处理
        state.ui_message = (
            "❌ 设置题目失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        cl.user_session.set("state", state)
        await cl.Message(
            content=state.ui_message,
            actions=stage_actions(state)
        ).send()


@cl.action_callback("view_problem")
async def on_view_problem(action: cl.Action):
    """
    处理查看题目
    """
    state: CoachState = cl.user_session.get("state")
    
    content = problem_service.format_problem_for_display(state.problem)
    await cl.Message(content=content).send()


@cl.action_callback("confirm_problem")
async def on_confirm_problem(action: cl.Action):
    """
    处理确认题目
    """
    state: CoachState = cl.user_session.get("state")
    
    try:
        # 确认题目，进入思路阶段
        state.phase = "thinking"
        from coach.services import GraphService
        graph_service = GraphService()
        state = graph_service.run_graph(state)
        
        # 更新会话状态
        cl.user_session.set("state", state)
        
        # 发送响应
        await cl.Message(
            content=state.ui_message,
            actions=stage_actions(state)
        ).send()
    except Exception as e:
        print(f"Error in on_confirm_problem: {e}")
        import traceback
        traceback.print_exc()
        
        # 错误处理
        state.ui_message = (
            "❌ 确认题目失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        cl.user_session.set("state", state)
        await cl.Message(
            content=state.ui_message,
            actions=stage_actions(state)
        ).send()

@cl.action_callback("reset_problem")
async def on_reset_problem(action: cl.Action):
    """
    处理重新设置题目
    """
    state: CoachState = cl.user_session.get("state")
    
    try:
        # 直接调用设置题目的回调
        await on_set_problem(action)
    except Exception as e:
        print(f"Error in on_reset_problem: {e}")
        import traceback
        traceback.print_exc()
        
        # 错误处理
        state.ui_message = (
            "❌ 重新设置题目失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试，或检查你的输入是否正确。"
        )
        
        cl.user_session.set("state", state)
        await cl.Message(
            content=state.ui_message,
            actions=stage_actions(state)
        ).send()

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
        # 使用动作处理器路由到对应处理函数
        updated_state = await action_handler.route_action(state, action)
        
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
