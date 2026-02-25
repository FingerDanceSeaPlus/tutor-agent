# coach/graph.py
from __future__ import annotations
from langgraph.graph import StateGraph, END
from coach.schemas import CoachState
from coach.subgraphs.problem_setup import build_problem_setup_subgraph
from coach.subgraphs.thinking import build_thinking_subgraph
from coach.subgraphs.coding import build_coding_subgraph
from coach.subgraphs.testing import build_testing_subgraph
from coach.subgraphs.reflect import build_reflect_subgraph

# 构建子图
problem_setup_subgraph = build_problem_setup_subgraph()
thinking_subgraph = build_thinking_subgraph()
coding_subgraph = build_coding_subgraph()
testing_subgraph = build_testing_subgraph()
reflect_subgraph = build_reflect_subgraph()

# 顶层路由函数
def top_level_router(state: CoachState) -> str:
    """
    顶层路由函数，根据当前phase选择要调用的子图
    """
    print(f"TopLevelRouter: current phase = {state.phase}")
    
    if state.phase == "need_problem":
        return "problem_setup"
    elif state.phase == "thinking":
        return "thinking"
    elif state.phase == "coding":
        return "coding"
    elif state.phase == "testing":
        return "testing"
    elif state.phase == "reflecting":
        return "reflect"
    else:
        return "problem_setup"

def build_tutor_agent_graph():
    """
    构建顶层TutorAgentGraph
    """
    print("Building TutorAgentGraph...")
    
    # 创建顶层状态图
    graph = StateGraph(CoachState)
    
    # 添加子图作为节点
    graph.add_node("problem_setup", problem_setup_subgraph)
    graph.add_node("thinking", thinking_subgraph)
    graph.add_node("coding", coding_subgraph)
    graph.add_node("testing", testing_subgraph)
    graph.add_node("reflect", reflect_subgraph)
    
    # 设置入口点
    graph.set_entry_point("problem_setup")
    
    # 添加条件边，根据phase路由到不同的子图
    graph.add_conditional_edges("problem_setup", top_level_router, {
        "problem_setup": "problem_setup",
        "thinking": "thinking",
        "coding": "coding",
        "testing": "testing",
        "reflect": "reflect",
    })
    
    graph.add_conditional_edges("thinking", top_level_router, {
        "problem_setup": "problem_setup",
        "thinking": "thinking",
        "coding": "coding",
        "testing": "testing",
        "reflect": "reflect",
    })
    
    graph.add_conditional_edges("coding", top_level_router, {
        "problem_setup": "problem_setup",
        "thinking": "thinking",
        "coding": "coding",
        "testing": "testing",
        "reflect": "reflect",
    })
    
    graph.add_conditional_edges("testing", top_level_router, {
        "problem_setup": "problem_setup",
        "thinking": "thinking",
        "coding": "coding",
        "testing": "testing",
        "reflect": "reflect",
    })
    
    graph.add_conditional_edges("reflect", top_level_router, {
        "problem_setup": "problem_setup",
        "thinking": "thinking",
        "coding": "coding",
        "testing": "testing",
        "reflect": "reflect",
    })
    
    return graph.compile()

# 保持向后兼容
build_graph = build_tutor_agent_graph
