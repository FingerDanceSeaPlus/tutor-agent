from langgraph.graph import StateGraph, END
from typing import Dict, Any
from ...schemas.state import CoachState, TestReport, TestCaseResult
from ...schemas.stage import Stage
from ...services.runner_service import RunnerService


class TestingSubGraph:
    """测试子图"""
    def __init__(self):
        self.name = "testing"
        self.runner_service = RunnerService()

    def build(self) -> StateGraph:
        """构建子图"""
        graph = StateGraph(CoachState)

        # 添加节点
        graph.add_node("generate_test_cases", self.generate_test_cases)
        graph.add_node("run_tests", self.run_tests)
        graph.add_node("analyze_results", self.analyze_results)

        # 添加边
        graph.set_entry_point("generate_test_cases")
        graph.add_edge("generate_test_cases", "run_tests")
        graph.add_edge("run_tests", "analyze_results")
        graph.add_edge("analyze_results", END)

        return graph

    async def generate_test_cases(self, state: CoachState) -> Dict[str, Any]:
        """生成测试用例"""
        # 生成测试用例
        # 这里简化处理，实际实现需要根据题目生成测试用例
        test_cases = [
            {"input": "测试输入1", "expected": "期望输出1"},
            {"input": "测试输入2", "expected": "期望输出2"},
            {"input": "边界输入", "expected": "边界输出"}
        ]

        return {"test_cases": test_cases}

    async def run_tests(self, state: CoachState) -> Dict[str, Any]:
        """运行测试"""
        code = state.code
        if not code:
            return {"test_report": None}

        test_cases = getattr(state, "test_cases", [])
        results = []

        # 运行测试用例
        # 这里简化处理，实际实现需要调用Runner服务
        for test_case in test_cases:
            try:
                # 模拟运行测试
                actual = "实际输出"
                passed = actual == test_case["expected"]
                result = TestCaseResult(
                    input=test_case["input"],
                    expected=test_case["expected"],
                    actual=actual,
                    passed=passed,
                    execution_time=0.05
                )
                results.append(result)
            except Exception as e:
                result = TestCaseResult(
                    input=test_case["input"],
                    expected=test_case["expected"],
                    actual=str(e),
                    passed=False,
                    execution_time=None
                )
                results.append(result)

        # 构建测试报告
        passed = all(r.passed for r in results)
        test_report = TestReport(
            passed=passed,
            results=results,
            total_time=sum(r.execution_time or 0 for r in results),
            memory_usage=10.0,
            failure_category="WA" if not passed else None
        )

        return {"test_report": test_report}

    async def analyze_results(self, state: CoachState) -> Dict[str, Any]:
        """分析测试结果"""
        test_report = state.test_report
        if not test_report:
            return {}

        # 分析测试结果，生成详细报告
        # 这里简化处理，实际实现需要更复杂的分析逻辑
        if not test_report.passed:
            # 找出失败的测试用例
            failed_cases = [r for r in test_report.results if not r.passed]
            failure_reason = f"测试失败，共{len(failed_cases)}个测试用例未通过"
        else:
            failure_reason = "所有测试用例通过"

        return {
            "transition_reason": failure_reason
        }
