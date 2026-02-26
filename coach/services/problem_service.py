from coach.schemas import Problem
from coach.problem_parser import parse_examples_from_text, summarize_title, extract_constraints
from typing import List, Dict

class ProblemService:
    """
    题目处理服务
    负责题目的解析和处理
    """
    
    def __init__(self):
        pass
    
    def parse_problem(self, raw_text: str) -> Problem:
        """
        解析题目文本
        """
        try:
            cases = parse_examples_from_text(raw_text)
            title = summarize_title(raw_text)
            constraints = extract_constraints(raw_text)
            
            # 创建问题对象
            problem = Problem(
                source="custom",
                id="custom-001",
                title=title,
                statement=raw_text[:1200],  # 展示截断；完整保存在 raw_text
                raw_text=raw_text,
                constraints=constraints,
                testcases=cases,
                examples="\n---\n".join(
                    [f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in cases[:5]]
                )
            )
            
            return problem
        except Exception as e:
            print(f"Error parsing problem: {e}")
            # 返回空问题对象
            return Problem(
                source="custom",
                id="custom-001",
                title="解析失败",
                statement="题目解析失败，请检查输入格式。",
                raw_text=raw_text,
                constraints="",
                examples="",
                testcases=[]
            )
    
    def validate_problem(self, problem: Problem) -> bool:
        """
        验证题目是否有效
        """
        try:
            return bool(
                problem.title and 
                problem.statement and 
                problem.raw_text
            )
        except Exception:
            return False
    
    def format_problem_for_display(self, problem: Problem) -> str:
        """
        格式化题目用于显示
        """
        content = f"### {problem.title}\n\n"
        content += f"**题目描述**：\n{problem.statement}\n\n"
        content += f"**约束条件**：\n{problem.constraints or '无'}\n\n"
        content += f"**样例**：\n{problem.examples or '无'}"
        return content
