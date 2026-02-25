# coach/subgraphs/testing.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from coach.tools_exec import run_tests

def run_test_cases(state: CoachState) -> CoachState:
    """
    运行测试用例，评估代码正确性
    """
    print("TestingSubgraph: run_test_cases")
    
    try:
        # 检查是否有测试用例
        if not state.problem.testcases:
            state.ui_message = (
                "当前题目没有测试用例。\n\n"
                "请确保题目文本中包含明确的样例输入输出，例如：\n\n"
                "输入：\n1\n2\n输出：\n3\n\n"
                "或使用 --- 分隔多个样例。"
            )
            return state
        
        # 检查是否有代码
        if not state.user_attempt.code:
            state.ui_message = (
                "请先提交你的代码实现。\n\n"
                "请确保：\n"
                "- 定义 `solve(inp: str) -> str` 函数\n"
                "- 正确处理输入输出格式\n"
                "- 考虑所有边界条件"
            )
            state.phase = "coding"
            return state
        
        # 运行测试用例
        result = run_tests(state.user_attempt.code, state.problem.testcases)
        state.evaluation.passed = result["passed"]
        state.evaluation.failing_cases = result["failing"]
        
        # 记录测试运行
        state.user_attempt.tests_run.append(f"测试运行: {len(result['failing'])} 个失败用例")
        
        # 根据测试结果决定下一步
        if state.evaluation.passed:
            state.ui_message = (
                "✅ 所有测试用例通过！\n\n"
                f"你成功通过了 {len(state.problem.testcases)} 个测试用例。\n\n"
                "你的代码成功解决了这个问题。现在可以进入复盘阶段，总结解题经验。"
            )
            state.phase = "reflecting"
        else:
            # 处理失败情况
            total_cases = len(state.problem.testcases)
            passed_cases = total_cases - len(result["failing"])
            
            state.ui_message = (
                f"❌ 测试用例失败\n\n"
                f"**测试结果**：{passed_cases}/{total_cases} 个用例通过\n\n"
            )
            
            # 显示前3个失败用例
            for i, failure in enumerate(result["failing"][:3]):
                if "error" in failure:
                    # 运行时错误
                    state.ui_message += (
                        f"**Case {failure['case']} 运行时错误**：\n"
                        f"```text\n{failure['error'][:500]}{'...' if len(failure['error']) > 500 else ''}\n```\n\n"
                    )
                else:
                    # 输出不匹配
                    state.ui_message += (
                        f"**Case {failure['case']} 输出不匹配**\n"
                        f"- 输入：\n```text\n{failure['input'][:200]}{'...' if len(failure['input']) > 200 else ''}\n```\n"
                        f"- 期望：\n```text\n{failure['expected'][:200]}{'...' if len(failure['expected']) > 200 else ''}\n```\n"
                        f"- 实际：\n```text\n{failure['got'][:200]}{'...' if len(failure['got']) > 200 else ''}\n```\n\n"
                    )
            
            # 添加失败原因分析
            state.ui_message += (
                "**失败原因分析**：\n"
                "- 边界条件处理错误：检查是否正确处理了空输入、极值等情况\n"
                "- 输入输出格式错误：检查是否正确解析输入和格式化输出\n"
                "- 逻辑算法错误：检查算法思路是否正确\n"
                "- 变量初始化错误：检查变量是否正确初始化\n"
                "- 异常处理错误：检查是否正确处理可能的异常情况\n\n"
                "请分析失败原因，并进行最小修改。"
            )
            
            # 增加重试次数
            state.progress.retry_count += 1
            
            # 保持在coding阶段，让用户修复代码
            state.phase = "coding"
    except Exception as e:
        print(f"Error in test execution: {e}")
        state.ui_message = (
            "❌ 测试执行失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请检查你的代码是否有语法错误或其他问题。"
        )
        state.phase = "coding"
    
    return state

def build_testing_subgraph():
    """
    构建TestingSubgraph子图
    """
    graph = StateGraph(CoachState)
    graph.add_node("run_test_cases", run_test_cases)
    
    graph.set_entry_point("run_test_cases")
    graph.add_edge("run_test_cases", END)
    
    return graph.compile()