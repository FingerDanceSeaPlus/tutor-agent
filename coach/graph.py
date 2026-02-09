# coach/graph.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from coach.tools_exec import run_tests, default_plan_steps
from coach.hint_policy import HintPolicy, format_hint_header, hint_rules

# ---------- Nodes ----------

def n_intake(state: CoachState) -> CoachState:
    state.step.name = "intake"
    state.step.status = "done"
    state.ui_message = (
        "我会按“教学模式”带你刷题：**先思路后代码**，并且提示按等级递增。\n\n"
        "请先在「我的思路」里提交：\n"
        "1) 你对题意的复述\n"
        "2) 关键约束/边界\n"
        "3) 你打算用的算法（不确定也可以写猜测）\n"
    )
    state.next_action = "diagnose"
    return state

def n_diagnose(state: CoachState) -> CoachState:
    state.step.name = "diagnose"
    state.step.status = "done"
    # MVP：不做复杂分类，后续可用 LLM/题库标签
    state.analysis.topic_tags = state.analysis.topic_tags or ["unknown"]
    state.plan.steps = state.plan.steps or default_plan_steps()
    state.plan.milestone = "完成伪码 + 不变量 + 复杂度"
    state.ui_message = (
        "### 计划\n" +
        "\n".join([f"- {i+1}. {s}" for i, s in enumerate(state.plan.steps)]) +
        f"\n\n**当前里程碑**：{state.plan.milestone}\n\n"
        "现在请你提交：**伪码（3~8 行）+ 不变量 + 复杂度**（写在「我的思路」里）。"
    )
    state.next_action = "probe"
    return state

def n_probe(state: CoachState) -> CoachState:
    state.step.name = "probe"
    state.step.status = "need_user"
    # 关键：用苏格拉底式问题逼用户先说
    state.ui_message = (
        "### 关键问题（先回答再写代码）\n"
        "1) 你的解法在每一步维护的 **不变量** 是什么？\n"
        "2) 最容易错的 **边界条件** 是哪些？至少列 3 个。\n"
        "3) 你的算法为什么满足复杂度要求？\n\n"
        "提交后我会根据你的回答决定：继续提示 / 给伪码修正 / 进入编码。"
    )
    state.next_action = "hint_or_advance"
    return state

def n_hint_or_advance(state: CoachState) -> CoachState:
    state.step.name = "hint_or_advance"
    state.step.status = "done"

    thoughts = (state.user_attempt.thoughts or "").strip()
    hp = HintPolicy(max_level=int(state.hint_policy.max_level),
                    final_answer_level=int(state.hint_policy.give_final_answer_at_level))

    # 判断是否“缺少关键要素”
    missing = []
    if "不变量" not in thoughts and "invariant" not in thoughts.lower():
        missing.append("不变量")
    if "复杂度" not in thoughts and "O(" not in thoughts:
        missing.append("复杂度")
    if len(thoughts) < 30:
        missing.append("思路太短")

    if missing:
        # 升级提示等级（但不跳级）
        state.hint_policy.level = hp.bump(int(state.hint_policy.level))  # type: ignore
        state.hint_policy.hint_count += 1

        lvl = int(state.hint_policy.level)
        state.ui_message = (
            format_hint_header(lvl) +
            hint_rules(lvl) +
            f"\n你当前缺少：**{', '.join(missing)}**。\n\n"
            "请补齐这三项（可直接用下面模板）：\n"
            "- 不变量：……\n"
            "- 边界：1) … 2) … 3) …\n"
            "- 复杂度：时间 O(?)，空间 O(?)，理由：……\n"
        )
        state.next_action = "probe"
        return state

    # 思路齐全 → 进入编码
    state.ui_message = (
        "好，现在进入编码。\n\n"
        "请在「代码」里实现：\n"
        "- 必须提供 `solve(inp: str) -> str`\n"
        "- 用换行读入/输出（你自行解析 inp）\n\n"
        "提交代码后点「运行测试」，我会给失败用例与纠错建议。"
    )
    state.next_action = "coach"
    return state

def n_coach(state: CoachState) -> CoachState:
    state.step.name = "coach"
    state.step.status = "need_user"

    if not (state.user_attempt.code or "").strip():
        state.ui_message = "请先提交代码（需要 `solve(inp: str) -> str`）。"
        state.next_action = "coach"
        return state

    # 先做轻量 code review（MVP：只做规范检查）
    msg = []
    if "def solve" not in state.user_attempt.code:
        msg.append("- 你没有定义 `solve(inp: str) -> str`。")
    if msg:
        state.ui_message = "### 代码规范问题\n" + "\n".join(msg)
        state.next_action = "coach"
        return state

    state.ui_message = "收到代码。现在请点「运行测试」。"
    state.next_action = "evaluate"
    return state

def n_evaluate(state: CoachState) -> CoachState:
    state.step.name = "evaluate"
    state.step.status = "running"

    # MVP：用 problem.examples 里预置的测试（你后续可接题库解析）
    # 这里演示：允许在 state.problem.examples 放 JSON-like 的测试用例（最简）
    # 若为空，就只提示用户添加测试
    testcases = []
    if state.problem.examples.strip():
        # 约定 examples 格式：
        # INPUT:
        # ...
        # OUTPUT:
        # ...
        # --- 分隔多个 case
        blocks = state.problem.examples.split("\n---\n")
        for b in blocks:
            if "INPUT:" in b and "OUTPUT:" in b:
                inp = b.split("INPUT:", 1)[1].split("OUTPUT:", 1)[0].strip() + "\n"
                out = b.split("OUTPUT:", 1)[1].strip() + "\n"
                testcases.append({"input": inp, "expected": out})

    if not testcases:
        state.evaluation.passed = False
        state.ui_message = (
            "当前题目没有内置测试样例（examples 为空或格式不对）。\n\n"
            "请你补充至少 1 个样例（INPUT/OUTPUT），或你贴出题目样例，我来结构化成测试。"
        )
        state.step.status = "done"
        state.next_action = "reflect"
        return state

    res = run_tests(state.user_attempt.code, testcases)
    state.evaluation.passed = bool(res["passed"])
    state.evaluation.failing_cases = res["failing"]
    state.step.status = "done"

    if state.evaluation.passed:
        state.ui_message = (
            "✅ **样例测试通过**。\n\n"
            "下一步：我会给你 3 类边界检查点，并生成 1~2 道变式训练。"
        )
        state.next_action = "reflect"
        return state

    # 失败：输出失败用例 + 纠错动作
    fc = state.evaluation.failing_cases[0]
    if "error" in fc:
        err = fc["error"]
        state.ui_message = (
            "❌ 运行时报错（先修复再谈逻辑）。\n\n"
            f"**Case {fc['case']} 报错**：\n```text\n{err}\n```\n"
            "请你：\n"
            "1) 标注你认为报错发生的位置（行号/代码片段）\n"
            "2) 给出你修复后的代码再跑一次\n"
        )
    else:
        state.ui_message = (
            "❌ 输出不匹配。\n\n"
            f"**Case {fc['case']}**\n"
            f"- 输入：\n```text\n{fc['input']}\n```\n"
            f"- 期望：\n```text\n{fc['expected']}\n```\n"
            f"- 实际：\n```text\n{fc['got']}\n```\n\n"
            "请你先回答：你认为是哪一类问题？（边界/初始化/循环条件/状态转移/输出格式）\n"
            "然后给出一个最小修改（不要重写）。"
        )
    state.next_action = "coach"
    state.progress.retry_count += 1
    return state

def n_reflect(state: CoachState) -> CoachState:
    state.step.name = "reflect"
    state.step.status = "done"

    if state.evaluation.passed:
        state.artifacts.cheat_sheet = (
            "模板：\n"
            "- 题意复述：…\n"
            "- 关键约束：…\n"
            "- 不变量：…\n"
            "- 边界三类：最小/极值/结构对抗\n"
            "- 复杂度：…\n"
        )
        state.progress.mastery_score = min(1.0, state.progress.mastery_score + 0.1)
        state.ui_message = (
            "### 复盘\n"
            "- 你本题的核心不变量是什么？用一句话写下来。\n"
            "- 最容易错的边界：最小输入、极值、结构对抗（各写 1 个）。\n\n"
            "### 解题卡（保存用）\n"
            f"```text\n{state.artifacts.cheat_sheet}\n```\n"
            "如果你把题目原文贴完整，我可以给你更具体的“变式题”与迁移训练路径。"
        )
    else:
        state.ui_message = (
            "### 当前未通过\n"
            "建议你先把“错因分类”写清楚，再做最小修改。\n\n"
            "可用模板：\n"
            "- 失败类型：边界/初始化/循环条件/状态转移/输出格式\n"
            "- 我预计的修复：改哪里？为什么？\n"
        )

    # 一轮结束，回到 probe 或 coach 取决于通过与否
    state.next_action = "probe" if state.evaluation.passed else "coach"
    return state

# ---------- Router ----------

def route(state: CoachState) -> str:
    na = state.next_action
    if na == "diagnose":
        return "diagnose"
    if na == "probe":
        return "probe"
    if na == "hint_or_advance":
        return "hint_or_advance"
    if na == "coach":
        return "coach"
    if na == "evaluate":
        return "evaluate"
    if na == "reflect":
        return "reflect"
    return "reflect"

def build_graph():
    g = StateGraph(CoachState)
    g.add_node("intake", n_intake)
    g.add_node("diagnose", n_diagnose)
    g.add_node("probe", n_probe)
    g.add_node("hint_or_advance", n_hint_or_advance)
    g.add_node("coach", n_coach)
    g.add_node("evaluate", n_evaluate)
    g.add_node("reflect", n_reflect)

    g.set_entry_point("intake")
    g.add_conditional_edges("intake", route, {
        "diagnose": "diagnose",
        "probe": "probe",
        "hint_or_advance": "hint_or_advance",
        "coach": "coach",
        "evaluate": "evaluate",
        "reflect": "reflect",
    })
    g.add_conditional_edges("diagnose", route, {
        "probe": "probe",
        "coach": "coach",
        "reflect": "reflect",
    })
    g.add_conditional_edges("probe", route, {
        "hint_or_advance": "hint_or_advance",
        "probe": "probe",
        "coach": "coach",
    })
    g.add_conditional_edges("hint_or_advance", route, {
        "probe": "probe",
        "coach": "coach",
    })
    g.add_conditional_edges("coach", route, {
        "evaluate": "evaluate",
        "coach": "coach",
    })
    g.add_conditional_edges("evaluate", route, {
        "reflect": "reflect",
        "coach": "coach",
    })
    g.add_conditional_edges("reflect", route, {
        "probe": "probe",
        "coach": "coach",
        "reflect": END,
    })

    return g.compile()
