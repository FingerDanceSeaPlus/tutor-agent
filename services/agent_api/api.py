from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, Any
import uuid
from graphs.main import TutorAgentGraph
from schemas.state import CoachState, Event


app = FastAPI()

# 配置CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 在生产环境中应该设置具体的域名
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 会话管理
sessions = {}

# 创建图实例
graph = TutorAgentGraph()
compiled_graph = graph.compile()


class SessionCreate(BaseModel):
    """创建会话请求"""
    pass


class SessionResponse(BaseModel):
    """创建会话响应"""
    session_id: str
    stage: str
    ui_hints: Dict[str, Any]


class EventRequest(BaseModel):
    """事件请求"""
    session_id: str
    event: Event


class EventResponse(BaseModel):
    """事件响应"""
    response: Dict[str, Any]
    stage: str


@app.post("/sessions", response_model=SessionResponse)
async def create_session(request: SessionCreate):
    """创建新会话"""
    # 生成会话ID
    session_id = str(uuid.uuid4())
    
    # 创建初始状态
    initial_state = CoachState(session_id=session_id)
    
    # 保存会话
    sessions[session_id] = {
        "state": initial_state,
        "created_at": uuid.uuid4().time
    }
    
    # 返回响应
    return SessionResponse(
        session_id=session_id,
        stage=initial_state.stage.value,
        ui_hints={}
    )


@app.post("/events", response_model=EventResponse)
async def handle_event(request: EventRequest):
    """处理用户事件"""
    session_id = request.session_id
    event = request.event
    print(sessions)
    print(session_id)
    # 检查会话是否存在
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 获取当前状态
    current_state = sessions[session_id]["state"]
    
    # 更新状态
    if event.type == "TEXT":
        current_state.user_input = event.payload.get("content", "")
    elif event.type == "ACTION":
        current_state.user_input = event.payload.get("action", "")
    
    # 运行图
    result = await compiled_graph.ainvoke(current_state.model_dump())
    
    # 更新会话状态
    new_state = CoachState(**result)
    sessions[session_id]["state"] = new_state
    
    # 生成响应
    response = result.get("response", {"content": "", "buttons": []})
    
    return EventResponse(
        response=response,
        stage=new_state.stage.value
    )


@app.get("/stream")
async def stream_events(session_id: str):
    """流式响应事件"""
    # 检查会话是否存在
    if session_id not in sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # 这里简化处理，实际实现需要使用SSE或WebSocket
    # 暂时返回当前状态
    current_state = sessions[session_id]["state"]
    
    return {
        "stage": current_state.stage.value,
        "message": "Stream endpoint not fully implemented"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002)
