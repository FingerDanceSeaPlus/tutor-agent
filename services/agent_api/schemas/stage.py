from enum import Enum


class Stage(Enum):
    """阶段枚举"""
    S1_PROBLEM = "S1_PROBLEM"  # 提交题目（含纠错、补全）
    S2_IDEA = "S2_IDEA"        # 提交思路（引导 + 纠偏）
    S3_CODE = "S3_CODE"        # 提交代码（格式检查 + 示例运行）
    S4_TEST = "S4_TEST"        # 测试（用例库/生成用例 + 性能信息 + 不过则回退）
    S5_REVIEW = "S5_REVIEW"    # 总结与复结（薄弱点 + 建议 + 后续计划）


    def next(self):
        """获取下一个阶段"""
        stages = list(Stage)
        current_index = stages.index(self)
        if current_index < len(stages) - 1:
            return stages[current_index + 1]
        return self

    def prev(self):
        """获取上一个阶段"""
        stages = list(Stage)
        current_index = stages.index(self)
        if current_index > 0:
            return stages[current_index - 1]
        return self
