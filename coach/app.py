# coach/app.py
from __future__ import annotations
import chainlit as cl
from coach.schemas import CoachState, Problem
from coach.graph import build_graph

GRAPH = build_graph()

def init_state() -> CoachState:
    # MVP：用一个示例题。你后续接入题库时，替换 Problem 的来源即可。
    p = Problem(
        source="custom",
        id="demo-001",
        title="Echo",
        statement="实现 solve(inp) 原样输出输入（用于验证系统链路）。",
        constraints="任意文本",
        examples="INPUT:\nhello\nOUTPUT:\nhello\n"
    )
    return CoachState(problem=p)

async def render(state: CoachState):
    await cl.Message(content=state.ui_message).send()

async def run_graph_once(state: CoachState) -> CoachState:
    # LangGraph 支持 dict；这里用 model_dump / model_validate 来回转换更稳
    out = GRAPH.invoke(state.model_dump())
    return CoachState.model_validate(out)

@cl.on_chat_start
async def on_start():
    state = init_state()
    state = await run_graph_once(state)
    cl.user_session.set("state", state)

    # 动作按钮
    actions = [
        cl.Action(name="need_hint", value="need_hint", label="我想要提示"),
        cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"),
        cl.Action(name="submit_code", value="submit_code", label="提交代码"),
        cl.Action(name="run_tests", value="run_tests", label="运行测试"),
    ]
    await render(state)
    await cl.Message(content="选择一个动作：", actions=actions).send()

@cl.on_action
async def on_action(action: cl.Action):
    state: CoachState = cl.user_session.get("state")

    if action.name == "need_hint":
        # 用户主动要提示：直接 bump level + 回到 probe
        state.hint_policy.hint_count += 1
        if int(state.hint_policy.level) < int(state.hint_policy.max_level):
            state.hint_policy.level = int(state.hint_policy.level) + 1  # type: ignore
        state.next_action = "probe"

    elif action.name == "submit_thoughts":
        res = await cl.AskUserMessage(
            content="把你的思路贴在这里（复述题意/约束/不变量/复杂度/伪码）。",
            timeout=300,
        ).send()
        if res:
            state.user_attempt.thoughts = res["output"]
        state.next_action = "hint_or_advance"

    elif action.name == "submit_code":
        res = await cl.AskUserMessage(
            content="把你的 Python 代码贴在这里（必须包含 solve(inp: str) -> str）。",
            timeout=300,
        ).send()
        if res:
            state.user_attempt.code = res["output"]
        state.next_action = "coach"

    elif action.name == "run_tests":
        state.next_action = "evaluate"

    # 跑图
    state = await run_graph_once(state)
    cl.user_session.set("state", state)
    await render(state)

    # 重新发一组按钮
    actions = [
        cl.Action(name="need_hint", value="need_hint", label="我想要提示"),
        cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"),
        cl.Action(name="submit_code", value="submit_code", label="提交代码"),
        cl.Action(name="run_tests", value="run_tests", label="运行测试"),
    ]
    await cl.Message(content="下一步：", actions=actions).send()
