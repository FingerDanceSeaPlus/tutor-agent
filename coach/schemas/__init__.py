from __future__ import annotations
from typing import Any, Dict, List, Optional, Literal
from pydantic import BaseModel, Field

HintLevel = Literal[0, 1, 2, 3, 4, 5]

class Problem(BaseModel):
    """
    问题类
    """
    source: str = "custom"
    id: str = "unknown"
    title: str = "Untitled"
    statement: str
    constraints: str = ""
    examples: str = ""      # 仍保留：展示用
    raw_text: str = ""      # 新增：完整题干
    testcases: List[Dict[str, str]] = Field(default_factory=list)  # 新增：评测用例

class UserAttempt(BaseModel):
    """
    用户尝试类
    """
    thoughts: str = ""          # 用户思路/不变量/复杂度
    code: str = ""              # 用户代码（单文件）
    tests_run: List[str] = Field(default_factory=list)
    errors: str = ""

class Analysis(BaseModel):
    """
    研究类
    """
    topic_tags: List[str] = Field(default_factory=list)
    difficulty_est: int = 2
    key_observations: List[str] = Field(default_factory=list)
    common_traps: List[str] = Field(default_factory=list)

class Plan(BaseModel):
    """
    计划类
    """
    steps: List[str] = Field(default_factory=list)
    milestone: str = ""

class HintPolicyState(BaseModel):
    level: HintLevel = 0
    max_level: HintLevel = 5
    give_final_answer_at_level: HintLevel = 5
    hint_count: int = 0

class Evaluation(BaseModel):
    passed: bool = False
    failing_cases: List[Dict[str, Any]] = Field(default_factory=list)
    feedback: List[str] = Field(default_factory=list)

class Artifacts(BaseModel):
    pseudocode: str = ""
    invariants: str = ""
    complexity: str = ""
    final_solution: str = ""
    cheat_sheet: str = ""

class Progress(BaseModel):
    mastery_score: float = 0.0
    retry_count: int = 0

class StepState(BaseModel):
    name: str = "intake"
    status: Literal["idle", "need_user", "running", "done"] = "idle"
    history: List[str] = Field(default_factory=list)

class CoachState(BaseModel):
    mode: Literal["tutor"] = "tutor"#Agent模式
    language: Literal["python"] = "python"
    phase: Literal["need_problem", "thinking", "coding", "testing", "reflecting"] = "need_problem"#阶段

    problem: Problem
    user_attempt: UserAttempt = Field(default_factory=UserAttempt)

    analysis: Analysis = Field(default_factory=Analysis)
    plan: Plan = Field(default_factory=Plan)

    hint_policy: HintPolicyState = Field(default_factory=HintPolicyState)

    evaluation: Evaluation = Field(default_factory=Evaluation)
    artifacts: Artifacts = Field(default_factory=Artifacts)
    progress: Progress = Field(default_factory=Progress)

    # 路由控制：节点之间传递“下一步要做什么”
    
    ui_message: str = ""            # 给 Chainlit 展示的主文本
    next_action: str = ""            # 路由控制

__all__ = [
    "CoachState",
    "Problem",
    "UserAttempt",
    "Analysis",
    "Plan",
    "HintPolicyState",
    "Evaluation",
    "Artifacts",
    "Progress",
    "StepState"
]
