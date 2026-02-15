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
    你当前 graph 用 next_action 驱动路由，所以这里主要看 next_action + 状态信号。
    """
    actions: List[cl.Action] = []

    # 0) 题目尚未设置：强制只显示“设置题目”（避免误操作）
    if not has_problem(state):
        actions.append(cl.Action(name="set_problem", value="set_problem", label="设置题目"))
        return actions

    # 通用按钮（但不要太多）
    actions.append(cl.Action(name="view_problem", value="view_problem", label="查看题目"))

    na = (state.next_action or "").strip()

    # 1) 思路阶段 / 探测阶段：强调“提交思路”
    if na in {"diagnose", "probe", "hint_or_advance"}:
        actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        # 如果已有思路，可直接推进（让用户显式点“继续”更像教学产品）
        if has_thoughts(state):
            actions.append(cl.Action(name="continue", value="continue", label="继续下一步"))
        return actions

    # 2) 编码阶段：强调“提交代码 / 运行测试”
    if na in {"coach"}:
        actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
        if has_code(state):
            actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
        actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        return actions

    # 3) 评测阶段：只给“运行测试”（以及必要时提交代码）
    if na in {"evaluate"}:
        if not has_code(state):
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
        actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
        return actions

    # 4) 复盘阶段：通过/未通过给不同按钮
    if na in {"reflect"}:
        if passed(state):
            actions.append(cl.Action(name="variant", value="variant", label="做变式题"))
            actions.append(cl.Action(name="next_problem", value="next_problem", label="下一题"))
        else:
            actions.append(cl.Action(name="submit_code", value="submit_code", label="提交修复代码"))
            actions.append(cl.Action(name="run_tests", value="run_tests", label="再跑测试"))
            actions.append(cl.Action(name="need_hint", value="need_hint", label=f"提示(L{int(state.hint_policy.level)})"))
        return actions

    # 兜底：给最小集合
    actions.append(cl.Action(name="submit_thoughts", value="submit_thoughts", label="提交思路"))
    actions.append(cl.Action(name="submit_code", value="submit_code", label="提交代码"))
    actions.append(cl.Action(name="run_tests", value="run_tests", label="运行测试"))
    return actions

async def render(state: CoachState, actions: List):
    await cl.Message(content=state.ui_message,actions=actions).send()

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
    await render(state,actions)
   

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
