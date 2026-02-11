# coach/app.py
from __future__ import annotations
import chainlit as cl
from coach.schemas import CoachState, Problem
from coach.graph import build_graph
from coach.problem_parser import *
GRAPH = build_graph()
from IPython.display import Image, display
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

async def render(state: CoachState):
    await cl.Message(content=state.ui_message).send()

async def run_graph_once(state: CoachState) -> CoachState:
    # LangGraph 支持 dict；这里用 model_dump / model_validate 来回转换更稳
    out = GRAPH.invoke(state.model_dump(),config={
        "recursion_limit": 25,
        "debug": True
    })
    return CoachState.model_validate(out)




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
    await render(state)
    await cl.Message(content=state.ui_message, actions=actions).send()


@cl.action_callback("coach")
async def on_action(action: cl.Action):
    state: CoachState = cl.user_session.get("state")

    actions = [
        cl.Action(name="need_hint", payload={"value": "example_value"},value="need_hint", label="我想要提示"),
        cl.Action(name="submit_thoughts", payload={"value": "example_value"},value="submit_thoughts", label="提交思路"),
        cl.Action(name="submit_code",payload={"value": "example_value"}, value="submit_code", label="提交代码"),
        cl.Action(name="run_tests", payload={"value": "example_value"},value="run_tests", label="运行测试"),
    ]

    res=await cl.AskUserMessage(
        content="请黏贴题目原文（包含样例 Input/Output）。",
        timeout=60000
    ).send()


    if res:
        raw=res["output"]
        cases=parse_examples_from_text(raw)
        title=summarize_title(raw)
        constraints=extract_constraints(raw)

        state.problem.raw_text=raw
        state.problem.title=title
        state.problem.statement = raw[:1200]  # MVP：展示截断；完整保存在 raw_text
        state.problem.constraints = constraints
        state.problem.testcases = cases
        state.problem.examples = "\n---\n".join(
                [f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in cases[:5]]
            )
        # 设置题目后，进入 intake→diagnose→probe
        state.next_action = "diagnose"

        out = GRAPH.invoke(state.model_dump())
        state = CoachState.model_validate(out)

        cl.user_session.set("state", state)
        await cl.Message(
                content=(
                    f"✅ 已设置题目：**{state.problem.title}**\n"
                    f"- 抽取到测试用例数：{len(state.problem.testcases)}\n\n"
                    + state.ui_message
                ),
                actions=actions
        ).send()
        return
        


    
    await render(state)
    await cl.Message(content="选择一个动作：", actions=actions).send()
"""
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
"""