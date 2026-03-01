from langgraph.graph import StateGraph, END
from typing import Dict, Any, Optional
from ..schemas.state import CoachState, Event, Message, TraceEvent
from ..schemas.stage import Stage


class SubGraph:
    """子图基类"""
    def __init__(self, name: str):
        self.name = name

    def build(self) -> StateGraph:
        """构建子图"""
        raise NotImplementedError


class BaseGraph:
    """基础图类"""
    def __init__(self):
        self.graph = StateGraph(CoachState)
        self._build_graph()

    def _build_graph(self):
        """构建图"""
        # 添加节点
        self.graph.add_node("ingest_user_input", self.ingest_user_input)
        self.graph.add_node("stage_router", self.stage_router)
        self.graph.add_node("render_response", self.render_response)
        self.graph.add_node("persist_trace", self.persist_trace)

        # 添加边
        self.graph.set_entry_point("ingest_user_input")
        self.graph.add_edge("ingest_user_input", "stage_router")
        self.graph.add_edge("render_response", "persist_trace")
        self.graph.add_edge("persist_trace", END)

    async def ingest_user_input(self, state: CoachState) -> Dict[str, Any]:
        """处理用户输入"""
        # 检查是否有用户输入
        if not state.user_input:
            return {}
        
        # 初始化事件和消息
        event = None
        user_message = None
        trace_event = None
        
        # 尝试解析输入类型
        input_data = self._parse_input(state.user_input)
        input_type = input_data.get("type", "TEXT")
        payload = input_data.get("payload", {})
        
        if input_type == "TEXT":
            # 处理文本输入
            text_content = payload.get("text", state.user_input)
            user_message = Message(
                role="user",
                content=text_content
            )
            event = Event(
                type="TEXT",
                payload={"text": text_content}
            )
            trace_event = TraceEvent(
                stage=state.stage,
                kind="USER_INPUT",
                payload={
                    "input_type": "TEXT",
                    "content": text_content
                }
            )
        
        elif input_type == "ACTION":
            # 处理动作输入
            action = payload.get("action", "")
            user_message = Message(
                role="user",
                content=f"Action: {action}"
            )
            event = Event(
                type="ACTION",
                payload={"action": action}
            )
            trace_event = TraceEvent(
                stage=state.stage,
                kind="USER_INPUT",
                payload={
                    "input_type": "ACTION",
                    "action": action
                }
            )
        
        elif input_type == "FILE":
            # 处理文件输入
            file_name = payload.get("file_name", "")
            file_content = payload.get("content", "")
            user_message = Message(
                role="user",
                content=f"File uploaded: {file_name}"
            )
            event = Event(
                type="FILE",
                payload={"file_name": file_name, "content": file_content}
            )
            trace_event = TraceEvent(
                stage=state.stage,
                kind="USER_INPUT",
                payload={
                    "input_type": "FILE",
                    "file_name": file_name
                }
            )
        
        # 构建返回的状态更新
        updated_state = {}
        
        if user_message:
            updated_state["history"] = state.history + [user_message]
        
        if trace_event:
            updated_state["trace"] = {
                "stages": state.trace.stages,
                "events": state.trace.events + [trace_event]
            }
        
        return updated_state
    
    def _parse_input(self, input_data: str) -> Dict[str, Any]:
        """解析输入数据，识别输入类型"""
        try:
            # 尝试解析为JSON
            import json
            parsed = json.loads(input_data)
            if isinstance(parsed, dict) and "type" in parsed:
                return parsed
        except:
            pass
        
        # 默认视为文本输入
        return {
            "type": "TEXT",
            "payload": {"text": input_data}
        }

    async def stage_router(self, state: CoachState) -> Dict[str, Any]:
        """阶段路由"""
        # 根据当前阶段和事件类型决定下一个节点
        # 这里实现智能路由逻辑
        return {}

    async def render_response(self, state: CoachState) -> Dict[str, Any]:
        """渲染响应"""
        # 生成响应内容和UI按钮建议
        return {}

    async def persist_trace(self, state: CoachState) -> Dict[str, Any]:
        """持久化trace"""
        # 将trace写入存储
        return {}

    def determine_next_node(self, state: CoachState, event: Event) -> str:
        """决定下一个节点"""
        # 路由优先级：用户显式指令 > 系统门控规则 > 输入类型识别
        if event.type == "ACTION":
            action = event.payload.get("action")
            if action == "BACK":
                return f"{state.stage.prev().value}_graph"
            elif action == "NEXT":
                # 检查是否满足进入下一步的条件
                if self._validate_state(state):
                    return f"{state.stage.next().value}_graph"
                return f"{state.stage.value}_graph"

        # 系统门控规则
        if state.stage == Stage.S4_TEST and state.test_report and not state.test_report.passed:
            return "S3_CODE_graph"
        elif state.stage == Stage.S3_CODE and state.run_report and not state.run_report.ok:
            return "S3_CODE_graph"
        elif state.stage == Stage.S1_PROBLEM and state.problem and not state.problem.ready:
            return "S1_PROBLEM_graph"

        # 默认留在当前阶段
        return f"{state.stage.value}_graph"

    def _validate_state(self, state: CoachState) -> bool:
        """验证状态是否满足进入下一步的条件"""
        if state.stage == Stage.S1_PROBLEM:
            return state.problem is not None and state.problem.ready
        elif state.stage == Stage.S2_IDEA:
            return state.idea is not None
        elif state.stage == Stage.S3_CODE:
            return state.code is not None and state.run_report and state.run_report.ok
        elif state.stage == Stage.S4_TEST:
            return state.test_report is not None and state.test_report.passed
        return True

    def transition_state(self, state: CoachState, next_stage: Stage, reason: str) -> CoachState:
        """状态转换"""
        state.stage = next_stage
        state.transition_reason = reason
        return state

    def compile(self):
        """编译图"""
        return self.graph.compile()
