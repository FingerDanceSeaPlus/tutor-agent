# coach/subgraphs/reflect.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState

def generate_reflection(state: CoachState) -> CoachState:
    """
    生成复盘卡，总结解题经验
    """
    print("ReflectSubgraph: generate_reflection")
    
    try:
        # 计算掌握度得分
        mastery_score = min(1.0, state.progress.mastery_score + 0.1)
        state.progress.mastery_score = mastery_score
        
        # 生成详细的解题卡
        state.artifacts.cheat_sheet = (
            f"# 解题卡：{state.problem.title}\n\n"
            f"## 题意复述\n"
            f"请用自己的话复述题目要求\n\n"
            f"## 关键约束\n"
            f"{state.problem.constraints or '未指定'}\n\n"
            f"## 不变量\n"
            f"请总结你的算法中的核心不变量\n\n"
            f"## 边界条件\n"
            f"- 最小输入\n"
            f"- 极值情况\n"
            f"- 结构对抗用例\n\n"
            f"## 复杂度分析\n"
            f"请分析时间和空间复杂度\n\n"
            f"## 解题思路\n"
            f"{state.user_attempt.thoughts or '未提交'}\n\n"
            f"## 代码实现\n"
            f"{state.user_attempt.code or '未提交'}\n\n"
            f"## 测试结果\n"
            f"- 通过测试用例数：{len(state.problem.testcases)}\n"
            f"- 重试次数：{state.progress.retry_count}\n"
            f"- 掌握度得分：{mastery_score:.2f}\n\n"
            f"## 复盘时间\n"
            f"{__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
        # 生成个性化复盘消息
        state.ui_message = (
            "### 复盘总结\n\n"
            "恭喜你完成了这道题！现在让我们来复盘一下：\n\n"
            "1. **核心不变量**：你的算法在每一步维护的关键性质是什么？\n"
            "2. **边界条件**：你遇到了哪些边界情况？是如何处理的？\n"
            "3. **改进空间**：你的代码还有哪些可以优化的地方？\n\n"
        )
        
        # 添加解题统计
        state.ui_message += (
            "### 解题统计\n\n"
            f"- 题目：{state.problem.title}\n"
            f"- 测试用例数：{len(state.problem.testcases)}\n"
            f"- 重试次数：{state.progress.retry_count}\n"
            f"- 掌握度得分：{mastery_score:.2f}\n"
            f"- 提示使用次数：{state.hint_policy.hint_count}\n\n"
        )
        
        # 添加解题卡
        state.ui_message += (
            "### 解题卡\n\n"
            f"```text\n{state.artifacts.cheat_sheet}\n```\n\n"
        )
        
        # 添加变式题建议
        state.ui_message += (
            "### 变式训练建议\n\n"
            "1. **修改约束条件**：尝试修改题目中的约束条件，看看你的算法是否仍然适用\n"
            "2. **增加维度**：如果是一维问题，尝试扩展到二维或更高维度\n"
            "3. **改变输入格式**：尝试使用不同的输入格式，如链表、树等数据结构\n"
            "4. **优化要求**：在时间或空间复杂度上提出更严格的要求\n\n"
        )
        
        # 添加知识点巩固建议
        state.ui_message += (
            "### 知识点巩固\n\n"
            "1. **相关算法**：复习与本题相关的算法和数据结构\n"
            "2. **常见错误**：总结本题中容易出现的错误类型\n"
            "3. **最佳实践**：学习相关的编码最佳实践\n"
            "4. **应用场景**：思考该算法在实际应用中的场景\n\n"
        )
        
        # 添加后续建议
        state.ui_message += (
            "### 后续建议\n\n"
            "1. **类似题目**：寻找具有相似解题思路的其他题目进行练习\n"
            "2. **代码重构**：尝试重构你的代码，提高可读性和效率\n"
            "3. **分享经验**：将你的解题经验分享给其他人\n"
            "4. **定期回顾**：定期回顾解题卡，巩固知识点\n\n"
            "如果你想继续刷题，可以粘贴新的题目文本开始新的练习。"
        )
        
        # 重置状态，准备下一题
        state.phase = "need_problem"
        
        # 保存最终解决方案
        state.artifacts.final_solution = state.user_attempt.code
        
    except Exception as e:
        print(f"Error in reflection generation: {e}")
        state.ui_message = (
            "❌ 复盘生成失败\n\n"
            f"错误信息：{str(e)}\n\n"
            "请稍后重试。"
        )
        state.phase = "need_problem"
    
    return state

def build_reflect_subgraph():
    """
    构建ReflectSubgraph子图
    """
    graph = StateGraph(CoachState)
    graph.add_node("generate_reflection", generate_reflection)
    
    graph.set_entry_point("generate_reflection")
    graph.add_edge("generate_reflection", END)
    
    return graph.compile()