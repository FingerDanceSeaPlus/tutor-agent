from pydantic import BaseModel, Field
from typing import List, Optional, Literal, Dict, Any
from datetime import datetime
from .stage import Stage


class Message(BaseModel):
    """消息模型"""
    role: Literal["user", "assistant", "system"]
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class CorrectionItem(BaseModel):
    """人工纠错记录"""
    field: str
    original: str
    corrected: str
    reason: str


class ProblemSpec(BaseModel):
    """题目标准化产物"""
    title: str
    description: str
    examples: List[Dict[str, Any]]
    constraints: List[str]
    input_format: Optional[str] = None
    output_format: Optional[str] = None
    tags: Optional[List[str]] = None
    errata: List[CorrectionItem] = Field(default_factory=list)
    ready: bool = False  # 是否满足进入下一步的条件


class IdeaSpec(BaseModel):
    """思路规格"""
    user_idea_raw: str
    analysis: str  # 对思路的评估：正确性、缺口
    guidance: str  # 下一步引导：按hint_level控制颗粒度
    key_invariants: Optional[List[str]] = None
    complexity: Optional[str] = None


class CodeSpec(BaseModel):
    """代码规格"""
    language: str
    code_text: str
    format_ok: bool
    entrypoint_detected: bool  # 是否存在可运行入口，如main / Solution
    last_edit_ts: datetime = Field(default_factory=datetime.utcnow)


class RunReport(BaseModel):
    """运行结果报告"""
    ok: bool
    output: str
    error: Optional[str] = None
    execution_time: Optional[float] = None


class TestCaseResult(BaseModel):
    """测试用例结果"""
    input: str
    expected: str
    actual: str
    passed: bool
    execution_time: Optional[float] = None


class TestReport(BaseModel):
    """测试结果报告"""
    passed: bool
    results: List[TestCaseResult]
    total_time: Optional[float] = None
    memory_usage: Optional[float] = None
    failure_category: Optional[Literal["WA", "TLE", "MLE", "RE"]] = None


class TraceEvent(BaseModel):
    """追踪事件"""
    ts: datetime = Field(default_factory=datetime.utcnow)
    stage: Stage
    kind: Literal["USER_INPUT", "ROUTE_DECISION", "VALIDATION_RESULT", "TOOL_CALL_START", "TOOL_CALL_END", "STAGE_OUTPUT", "ERROR"]
    payload: Dict[str, Any]


class StageTrace(BaseModel):
    """阶段追踪"""
    inputs: List[Message]
    decisions: List[Dict[str, Any]]
    tool_calls: List[Dict[str, Any]]
    outputs: Dict[str, Any]
    timestamps: Dict[str, datetime]


class TraceBundle(BaseModel):
    """复盘关键"""
    stages: Dict[Stage, StageTrace]
    events: List[TraceEvent]


class CoachState(BaseModel):
    """主状态"""
    stage: Stage = Stage.S1_PROBLEM
    hint_level: Literal["low", "mid", "high"] = "mid"
    problem: Optional[ProblemSpec] = None
    idea: Optional[IdeaSpec] = None
    code: Optional[CodeSpec] = None
    run_report: Optional[RunReport] = None
    test_report: Optional[TestReport] = None
    history: List[Message] = Field(default_factory=list)
    trace: TraceBundle = Field(default_factory=lambda: TraceBundle(stages={}, events=[]))
    session_id: Optional[str] = None
    phase_status: Optional[str] = None
    user_input: Optional[str] = None
    transition_reason: Optional[str] = None


class Event(BaseModel):
    """事件模型"""
    type: Literal["TEXT", "ACTION", "FILE"]
    payload: Dict[str, Any]
