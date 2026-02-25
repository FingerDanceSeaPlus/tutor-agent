# coach/subgraphs/thinking.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from coach.hint_policy import HintPolicy, format_hint_header, hint_rules

def guide_thinking(state: CoachState) -> CoachState:
    """
    Guide user to submit thinking
    """
    print("ThinkingSubgraph: guide_thinking")
    
    state.ui_message = (
        "### 思路分析\n\n"
        "请提交你的解题思路，包括：\n"
        "1) 你对题意的复述\n"
        "2) 关键约束/边界条件\n"
        "3) 你打算使用的算法\n"
        "4) 不变量分析\n"
        "5) 时间和空间复杂度分析"
    )
    
    return state

def check_thinking_completeness(state: CoachState) -> CoachState:
    """
    Check completeness of user's thinking, identify missing items
    """
    print("ThinkingSubgraph: check_thinking_completeness")
    
    try:
        thoughts = (state.user_attempt.thoughts or "").strip()
        
        # Check if thinking is empty
        if not thoughts:
            state.ui_message = (
                "请先提交你的解题思路，内容包括题意复述、关键约束、算法选择、不变量分析和复杂度分析。"
            )
            return state
        
        # Check if thinking contains key elements
        missing = []
        
        # 检查题意复述
        if "题意" not in thoughts and "复述" not in thoughts and "problem" not in thoughts.lower():
            missing.append("题意复述")
        
        # 检查关键约束
        if "约束" not in thoughts and "constraint" not in thoughts.lower():
            missing.append("关键约束分析")
        
        # 检查算法选择
        if "算法" not in thoughts and "algorithm" not in thoughts.lower():
            missing.append("算法选择")
        
        # 检查不变量分析
        if "不变量" not in thoughts and "invariant" not in thoughts.lower():
            missing.append("不变量分析")
        
        # 检查复杂度分析
        if "复杂度" not in thoughts and "O(" not in thoughts:
            missing.append("复杂度分析")
        
        # 检查边界条件分析
        if "边界" not in thoughts and "边界条件" not in thoughts and "edge case" not in thoughts.lower():
            missing.append("边界条件分析")
        
        # 检查思路长度
        if len(thoughts) < 50:
            missing.append("思路过于简略")
        
        # Decide next step based on missing items
        if missing:
            # Upgrade hint level
            hp = HintPolicy(
                max_level=int(state.hint_policy.max_level),
                final_answer_level=int(state.hint_policy.give_final_answer_at_level)
            )
            state.hint_policy.level = hp.bump(int(state.hint_policy.level))
            state.hint_policy.hint_count += 1
            
            lvl = int(state.hint_policy.level)
            state.ui_message = (
                format_hint_header(lvl) +
                hint_rules(lvl) +
                f"\n你当前缺少：**{', '.join(missing)}**。\n\n"
                "请补齐以下内容：\n"
                "- 题意复述：用自己的话描述题目要求\n"
                "- 关键约束：题目中的限制条件\n"
                "- 算法选择：你打算使用的算法及其理由\n"
                "- 不变量：算法在每一步维护的关键性质\n"
                "- 边界条件：最小输入、极值、结构对抗情况\n"
                "- 复杂度：时间 O(?)，空间 O(?)，理由：……"
            )
        else:
            # Thinking is complete, move to coding phase
            state.ui_message = (
                "✅ 思路分析完成！\n\n"
                "你的思路包含了所有关键要素，现在可以进入编码阶段。\n\n"
                "请在代码区域实现你的解决方案，确保：\n"
                "- 定义 `solve(inp: str) -> str` 函数\n"
                "- 正确处理输入输出格式\n"
                "- 考虑所有边界条件"
            )
            state.phase = "coding"
    except Exception as e:
        print(f"Error in check_thinking_completeness: {e}")
        state.ui_message = (
            "❌ 思路分析失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请重新提交你的解题思路。"
        )
    
    return state

def build_thinking_subgraph():
    """
    Build ThinkingSubgraph
    """
    graph = StateGraph(CoachState)
    graph.add_node("guide_thinking", guide_thinking)
    graph.add_node("check_thinking_completeness", check_thinking_completeness)
    
    graph.set_entry_point("guide_thinking")
    graph.add_edge("guide_thinking", "check_thinking_completeness")
    graph.add_edge("check_thinking_completeness", END)
    
    return graph.compile()