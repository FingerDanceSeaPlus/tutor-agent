from coach.graphs.subgraphs.problem_extraction import ProblemExtractionSubGraph
from coach.schemas import CoachState, Problem

# 创建测试状态
problem = Problem(statement="")
problem.raw_text = '''题目：两数之和
给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那两个整数，并返回它们的数组下标。
你可以假设每种输入只会对应一个答案。但是，数组中同一个元素不能使用两遍。
示例：
输入：nums = [2, 7, 11, 15], target = 9
输出：[0, 1]
解释：因为 nums[0] + nums[1] = 2 + 7 = 9，所以返回 [0, 1]。
约束条件：
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- 只会存在一个有效答案'''

state = CoachState(problem=problem)

# 测试提取功能
subgraph = ProblemExtractionSubGraph()
try:
    result = subgraph.extract_fields(state)
    print('提取结果:', result)
except Exception as e:
    print('错误:', str(e))
    import traceback
    traceback.print_exc()