# coach/subgraphs/coding.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState

def check_code_style(state: CoachState) -> CoachState:
    """
    Check user's code for compliance with requirements
    """
    print("CodingSubgraph: check_code_style")
    
    try:
        code = (state.user_attempt.code or "").strip()
        
        # Check if code is empty
        if not code:
            state.ui_message = (
                "请先提交你的代码实现。\n\n"
                "请确保：\n"
                "- 定义 `solve(inp: str) -> str` 函数\n"
                "- 正确处理输入输出格式\n"
                "- 考虑所有边界条件"
            )
            return state
        
        # Check for code style issues
        issues = []
        
        # 检查函数定义
        if "def solve" not in code:
            issues.append("缺少 `solve(inp: str) -> str` 函数定义")
        
        # 检查返回语句
        if "return" not in code:
            issues.append("缺少返回语句")
        
        # 检查代码长度
        if len(code) < 10:
            issues.append("代码过于简短，可能不完整")
        
        # 检查输入参数处理
        if "inp" not in code:
            issues.append("未使用输入参数 `inp`")
        
        # 检查代码缩进
        if code.count("\n    ") < code.count("\n") - 1:
            issues.append("代码缩进不规范，建议使用4个空格缩进")
        
        # 检查注释
        if "#" not in code:
            issues.append("建议添加代码注释，提高可读性")
        
        # 检查异常处理
        if "try" not in code and "except" not in code:
            issues.append("建议添加异常处理，提高代码健壮性")
        
        # 根据规范检查结果决定下一步
        if issues:
            state.ui_message = (
                "### 代码规范问题\n\n"
                "请修复以下问题：\n"
            )
            for issue in issues:
                state.ui_message += f"- {issue}\n"
            state.ui_message += "\n修复后再次提交代码。"
        else:
            state.ui_message = (
                "✅ 代码规范检查通过！\n\n"
                "现在可以运行测试来验证你的代码是否正确。\n\n"
                "请点击「运行测试」按钮，我会执行测试用例并给出反馈。"
            )
            state.phase = "testing"
    except Exception as e:
        print(f"Error in code style check: {e}")
        state.ui_message = (
            "❌ 代码检查失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请重新提交你的代码。"
        )
    
    return state

def build_coding_subgraph():
    """
    Build CodingSubgraph
    """
    graph = StateGraph(CoachState)
    graph.add_node("check_code_style", check_code_style)
    
    graph.set_entry_point("check_code_style")
    graph.add_edge("check_code_style", END)
    
    return graph.compile()