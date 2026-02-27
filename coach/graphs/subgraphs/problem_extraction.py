from coach.graphs.base import SubGraph
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from typing import Dict, Any
import json
import os
from coach.prompts import SYSTEM_PROMPT, PROBLEM_EXTRACTION_PROMPT
from coach.services.llm_service import LLMService
class ProblemExtractionSubGraph(SubGraph):
    """
    题目字段智能化提取子图
    使用LLM提取题目各个字段
    """
    
    def __init__(self):
        super().__init__("problem_extraction")
    
    def build(self) -> StateGraph:
        """
        构建题目提取子图
        """
        graph = StateGraph(CoachState)
        
        # 添加节点
        graph.add_node("extract_fields", self.extract_fields)
        graph.add_node("validate_extraction", self.validate_extraction)
        graph.add_node("process_results", self.process_results)
        graph.add_node("handle_error", self.handle_error)
        
        # 设置入口点
        graph.set_entry_point("extract_fields")
        
        # 添加条件边
        graph.add_conditional_edges(
            "extract_fields",
            self.determine_next_node,
            {
                "validate_extraction": "validate_extraction",
                "handle_error": "handle_error"
            }
        )
        
        graph.add_conditional_edges(
            "validate_extraction",
            self.determine_next_node,
            {
                "process_results": "process_results",
                "handle_error": "handle_error"
            }
        )
        
        graph.add_edge("process_results", END)
        graph.add_edge("handle_error", END)
        
        return graph
    
    def determine_next_node(self, state: CoachState) -> str:
        """
        根据状态决定下一步执行的节点
        """
        # 检查是否有错误
        if "error" in state.ui_message.lower():
            return "handle_error"
        
        # 根据当前节点和状态决定下一步
        # 这里可以根据具体的业务逻辑进行判断
        return "validate_extraction" if state.phase_status != "error" else "handle_error"
    
    def handle_error(self, state: CoachState) -> Dict[str, Any]:
        """
        处理错误
        """
        try:
            # 生成错误处理消息
            state.ui_message = (
                "❌ 题目提取过程中发生错误\n\n"
                "请检查你的输入是否正确，或稍后重试。\n\n"
                "你可以尝试重新设置题目。"
            )
            state.phase_status = "idle"
            return state.model_dump()
        except Exception as e:
            print(f"Error in handle_error: {e}")
            state.ui_message = "处理错误时发生异常，请重新设置题目。"
            state.phase_status = "idle"
            return state.model_dump()
    
    def extract_fields(self, state: CoachState) -> Dict[str, Any]:
        """
        使用LLM提取题目字段
        """
        try:
            problem_text = state.problem.raw_text
            
            # 检查环境变量
            api_key = os.getenv("DASHSCOPE_API_KEY")
            
            # 构建system prompt和user input
            system_prompt = SYSTEM_PROMPT
            
            user_input = PROBLEM_EXTRACTION_PROMPT.format(problem_text=problem_text)
            
            # 调用LLM - 使用LLM服务类，带重试和缓存机制
            llm_service = LLMService()
            agent_output = llm_service.invoke_with_retry(system_prompt, user_input)
            
            # 解析结果
            try:
                extraction_result = json.loads(agent_output)
            except Exception as e:
                # 尝试从输出中提取JSON部分
                import re
                # 尝试匹配完整的JSON对象，包括嵌套的
                json_match = re.search(r'\{[\s\S]*\}', agent_output)
                if json_match:
                    json_str = json_match.group(0)
                    try:
                        extraction_result = json.loads(json_str)
                    except Exception as e2:
                        # 尝试清理JSON字符串
                        json_str = json_str.replace('\\n', '').replace('\\t', '')
                        try:
                            extraction_result = json.loads(json_str)
                        except Exception as e3:
                            raise
                else:
                    raise
            
            # 更新状态
            state.problem.title = extraction_result.get("标题", state.problem.title)
            state.problem.statement = extraction_result.get("描述", state.problem.statement)
            
            # 处理约束条件 - 确保转换为字符串
            constraints = extraction_result.get("约束条件", state.problem.constraints)
            if isinstance(constraints, list):
                # 将列表转换为字符串，用换行符分隔
                state.problem.constraints = "\n".join(constraints)
            else:
                state.problem.constraints = constraints
            
            # 处理样例
            examples = extraction_result.get("样例", [])
            if examples:
                # 检查样例是否是单个对象还是数组
                if isinstance(examples, dict) and "input" in examples and "expected" in examples:
                    # 单个样例对象，转换为数组
                    state.problem.testcases = [examples]
                    examples_text = f"INPUT:\n{examples['input']}OUTPUT:\n{examples['expected']}"
                else:
                    # 样例数组
                    state.problem.testcases = examples
                    examples_text = "\n---\n".join([f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in examples[:5]])
                state.problem.examples = examples_text
            
            # 添加标签和难度信息到analysis
            state.analysis.topic_tags = extraction_result.get("标签", [])
            difficulty_map = {"简单": 1, "中等": 2, "困难": 3}
            state.analysis.difficulty_est = difficulty_map.get(extraction_result.get("难度", "中等"), 2)
            
            return state.model_dump()
        except Exception as e:
            print(f"Error in extract_fields: {e}")
            # 错误处理：使用原有解析逻辑作为回退
            from coach.problem_parser import parse_examples_from_text, extract_constraints, summarize_title
            
            state.problem.title = summarize_title(state.problem.raw_text)
            state.problem.constraints = extract_constraints(state.problem.raw_text)
            state.problem.testcases = parse_examples_from_text(state.problem.raw_text)
            
            if state.problem.testcases:
                examples_text = "\n---\n".join([f"INPUT:\n{c['input']}OUTPUT:\n{c['expected']}" for c in state.problem.testcases[:5]])
                state.problem.examples = examples_text
            
            return state.model_dump()
    
    def validate_extraction(self, state: CoachState) -> Dict[str, Any]:
        """
        验证提取结果
        """
        try:
            # 检查提取结果的完整性
            validation_result = {
                "has_title": bool(state.problem.title),
                "has_description": bool(state.problem.statement),
                "has_constraints": bool(state.problem.constraints),
                "has_examples": len(state.problem.testcases) > 0,
                "has_tags": len(state.analysis.topic_tags) > 0,
                "has_difficulty": state.analysis.difficulty_est > 0
            }
            
            # 验证样例格式
            for i, example in enumerate(state.problem.testcases):
                if "input" not in example or "expected" not in example:
                    validation_result[f"example_{i}_valid"] = False
                else:
                    validation_result[f"example_{i}_valid"] = True
            
            # 生成提取质量评估
            valid_count = sum(1 for v in validation_result.values() if isinstance(v, bool) and v)
            total_count = sum(1 for v in validation_result.values() if isinstance(v, bool))
            quality_score = valid_count / total_count if total_count > 0 else 0
            
            state.analysis.key_observations.append(f"提取质量评估：{quality_score:.2f}")
            
            return state.model_dump()
        except Exception as e:
            print(f"Error in validate_extraction: {e}")
            return state.model_dump()
    
    def process_results(self, state: CoachState) -> Dict[str, Any]:
        """
        处理和格式化提取结果
        """
        try:
            # 处理边界情况
            if not state.problem.title:
                state.problem.title = "未命名题目"
            
            if not state.problem.statement:
                state.problem.statement = state.problem.raw_text[:1200]
            
            if not state.problem.constraints:
                state.problem.constraints = "无"
            
            if not state.problem.examples:
                state.problem.examples = "无"
            
            # 生成提取完成的消息
            state.ui_message = (
                f"### 题目提取完成\n\n"
                f"**标题**：{state.problem.title}\n\n"
                f"**描述**：{state.problem.statement[:200]}...\n\n"
                f"**约束条件**：{state.problem.constraints}\n\n"
                f"**样例数量**：{len(state.problem.testcases)}\n\n"
                f"**标签**：{', '.join(state.analysis.topic_tags) if state.analysis.topic_tags else '无'}\n\n"
                f"**难度**：{'简单' if state.analysis.difficulty_est == 1 else '中等' if state.analysis.difficulty_est == 2 else '困难'}\n\n"
                "请检查以上信息是否正确，如需修改请重新设置题目。"
            )
            
            return state.model_dump()
        except Exception as e:
            print(f"Error in process_results: {e}")
            state.ui_message = "题目提取过程中发生错误，请重新尝试。"
            return state.model_dump()

# 构建函数
def build_problem_extraction_subgraph() -> StateGraph:
    """
    构建题目提取子图
    """
    subgraph = ProblemExtractionSubGraph()
    return subgraph.compile()
