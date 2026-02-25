# coach/subgraphs/problem_setup.py
from __future__ import annotations
import os
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field
from typing import List, Dict, Optional

class ParsedProblem(BaseModel):
    """
    解析后的题目信息模型
    """
    title: str = Field(..., description="题目标题")
    constraints: str = Field(..., description="题目约束条件")
    testcases: List[Dict[str, str]] = Field(..., description="测试用例列表，每个测试用例包含input和expected字段")
    statement: str = Field(..., description="题目描述，不包含样例部分")
    examples: str = Field(..., description="格式化的样例展示，用于用户查看")


def parse_problem_with_agent(raw_text: str) -> ParsedProblem:
    """
    使用LLM解析题目信息
    """
    try:
        # 创建输出解析器
        output_parser = PydanticOutputParser(pydantic_object=ParsedProblem)
        
        # 创建提示模板
        prompt = ChatPromptTemplate.from_template("""
        你是一个专业的编程题目解析助手，负责将原始题目文本解析为结构化的题目信息。
        
        请仔细分析以下题目文本，提取并结构化以下信息：
        1. 题目标题：简洁明了地概括题目的核心内容
        2. 约束条件：题目中提到的所有限制条件
        3. 测试用例：从题目中提取所有样例输入输出，格式为[{"input": "输入内容", "expected": "期望输出"}]
        4. 题目描述：题目文本中除了样例之外的部分，清晰描述问题要求
        5. 样例展示：将测试用例格式化为易读的形式，用于用户查看
        
        请确保：
        - 测试用例格式正确，每个测试用例包含input和expected字段
        - 题目描述不包含样例部分
        - 样例展示格式清晰，便于用户理解
        
        原始题目文本：
        {raw_text}
        
        {format_instructions}
        """)
        
        # 配置LLM
        llm = ChatOpenAI(api_key=os.getenv("DASHSCOPE_API_KEY"),
                         base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
                         model="qwen3-max"
        )
        
        # 绑定提示和解析器
        prompt_with_format = prompt.partial(format_instructions=output_parser.get_format_instructions())
        
        # 创建链
        chain = prompt_with_format | llm | output_parser
        
        # 执行链
        parsed_result = chain.invoke({"raw_text": raw_text})
        
        return parsed_result
    except Exception as e:
        print(f"Error in parse_problem_with_agent: {e}")
        # 返回默认值，确保系统不会崩溃
        return ParsedProblem(
            title="解析失败",
            constraints="",
            testcases=[],
            statement="题目解析失败，请检查题目格式",
            examples=""
        )


def setup_problem(state: CoachState) -> CoachState:
    """
    检查题目文本是否存在
    """
    print("ProblemSetup: setup_problem")
    
    # 检查是否有原始题目文本
    if not state.problem.raw_text:
        state.ui_message = (
            "请粘贴完整的题目文本，包括题目描述、输入输出格式、样例等。\n\n"
            "我会自动解析题目信息并生成测试用例。"
        )
        return state
    
    # 题目文本存在，继续解析
    state.ui_message = "正在解析题目信息..."
    return state

def parse_problem(state: CoachState) -> CoachState:
    """
    使用agent解析题目信息并更新状态
    """
    print("ProblemSetup: parse_problem")
    
    try:
        # 使用agent解析题目
        parsed_result = parse_problem_with_agent(state.problem.raw_text)
        
        # 更新状态
        state.problem.title = parsed_result.title
        state.problem.constraints = parsed_result.constraints
        state.problem.testcases = parsed_result.testcases
        state.problem.statement = parsed_result.statement[:1200]  # 截断过长的描述
        state.problem.examples = parsed_result.examples
        
        # 验证解析结果
        if not state.problem.testcases:
            state.ui_message = (
                f"已解析题目：{state.problem.title}\n\n"
                "但未找到有效的样例输入输出。请确保题目中包含明确的样例格式，例如：\n\n"
                "输入：\n1\n2\n输出：\n3\n\n"
                "或使用 --- 分隔多个样例。"
            )
        else:
            state.ui_message = (
                f"✅ 题目解析完成：{state.problem.title}\n\n"
                f"📋 约束条件：{state.problem.constraints or '未指定'}\n\n"
                f"🧪 生成了 {len(state.problem.testcases)} 个测试用例\n\n"
                "现在进入思路分析阶段，请提交你的解题思路。"
            )
            state.phase = "thinking"
    except Exception as e:
        print(f"Error in problem parsing: {e}")
        state.ui_message = (
            "❌ 题目解析失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请检查题目文本格式，确保包含完整的题目描述和样例输入输出。"
        )
    
    return state

def problem_setup_router(state: CoachState) -> str:
    """
    题目设置子图的路由函数
    """
    if not state.problem.raw_text:
        return "setup_problem"
    else:
        return "parse_problem"

def build_problem_setup_subgraph():
    """
    构建ProblemSetupSubgraph子图
    """
    graph = StateGraph(CoachState)
    
    # 添加节点
    graph.add_node("setup_problem", setup_problem)
    graph.add_node("parse_problem", parse_problem)
    
    # 设置入口点
    graph.set_entry_point("setup_problem")
    
    # 添加条件边
    graph.add_conditional_edges("setup_problem", problem_setup_router, {
        "setup_problem": "setup_problem",
        "parse_problem": "parse_problem"
    })
    
    # 解析完成后结束
    graph.add_edge("parse_problem", END)
    
    return graph.compile()