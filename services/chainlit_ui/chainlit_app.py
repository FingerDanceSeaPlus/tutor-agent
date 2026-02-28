import chainlit as cl
import httpx
import json
import uuid

# 后端API地址
AGENT_API_URL = "http://localhost:8002"

# 会话管理
sessions = {}


@cl.on_chat_start
async def on_chat_start():
    """聊天开始时的处理"""
    # 向后端创建会话
    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AGENT_API_URL}/sessions", json={})
        if response.status_code == 200:
            data = response.json()
            session_id = data.get("session_id")
            if session_id:
                cl.user_session.set("session_id", session_id)
                sessions[session_id] = {
                    "stage": data.get("stage"),
                    "ui_hints": data.get("ui_hints", [])
                }
                await cl.Message(content=f"欢迎使用算法编程学习助手！会话ID: {session_id}。请开始提交题目。").send()
            else:
                await cl.Message(content="获取会话ID失败，请刷新页面重试。").send()
        else:
            await cl.Message(content="连接后端服务失败，请稍后重试。").send()


@cl.on_message
async def on_message(message: cl.Message):
    """处理用户消息"""
    session_id = cl.user_session.get("session_id")
    if not session_id:
        await cl.Message(content="会话已过期，请刷新页面重新开始。").send()
        return

    # 发送用户输入到后端
    payload = {
        "session_id": session_id,
        "event": {
            "type": "TEXT",
            "payload": {
                "content": message.content
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AGENT_API_URL}/events", json=payload)
        if response.status_code == 200:
            data = response.json()
            # 处理后端响应
            await process_response(data)
        else:
            await cl.Message(content=f"处理请求失败，请稍后重试。错误码：{response.status_code}").send()


@cl.action_callback("NEXT")
async def on_next(action):
    """处理下一步操作"""
    await handle_action("NEXT", action)


@cl.action_callback("BACK")
async def on_back(action):
    """处理回退操作"""
    await handle_action("BACK", action)


@cl.action_callback("SET_HINT_LEVEL")
async def on_set_hint_level(action):
    """处理设置提示等级操作"""
    await handle_action("SET_HINT_LEVEL", action)


@cl.action_callback("RUN_EXAMPLES")
async def on_run_examples(action):
    """处理运行示例操作"""
    await handle_action("RUN_EXAMPLES", action)


@cl.action_callback("RUN_TESTS")
async def on_run_tests(action):
    """处理运行测试操作"""
    await handle_action("RUN_TESTS", action)


@cl.action_callback("EDIT_CONSTRAINTS")
async def on_edit_constraints(action):
    """处理编辑约束操作"""
    await handle_action("EDIT_CONSTRAINTS", action)


@cl.action_callback("EDIT_EXAMPLES")
async def on_edit_examples(action):
    """处理编辑示例操作"""
    await handle_action("EDIT_EXAMPLES", action)


@cl.action_callback("REQUEST_COUNTEREXAMPLE")
async def on_request_counterexample(action):
    """处理请求反例操作"""
    await handle_action("REQUEST_COUNTEREXAMPLE", action)


@cl.action_callback("FORMAT_CODE")
async def on_format_code(action):
    """处理格式化代码操作"""
    await handle_action("FORMAT_CODE", action)


@cl.action_callback("RUN_EDGE_TESTS")
async def on_run_edge_tests(action):
    """处理运行边界测试操作"""
    await handle_action("RUN_EDGE_TESTS", action)


@cl.action_callback("EXPORT_REPORT")
async def on_export_report(action):
    """处理导出报告操作"""
    await handle_action("EXPORT_REPORT", action)


@cl.action_callback("NEXT_PROBLEM")
async def on_next_problem(action):
    """处理下一题操作"""
    await handle_action("NEXT_PROBLEM", action)


async def handle_action(action_type, action):
    """处理按钮操作"""
    session_id = cl.user_session.get("session_id")
    if not session_id:
        await cl.Message(content="会话已过期，请刷新页面重新开始。").send()
        return

    # 发送操作到后端
    payload = {
        "session_id": session_id,
        "event": {
            "type": "ACTION",
            "payload": {
                "action": action_type,
                "data": action.get("payload", {})
            }
        }
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(f"{AGENT_API_URL}/events", json=payload)
        if response.status_code == 200:
            data = response.json()
            # 处理后端响应
            await process_response(data)
        else:
            await cl.Message(content=f"处理请求失败，请稍后重试。错误码：{response.status_code}").send()


async def process_response(data):
    """处理后端响应"""
    # 提取响应内容
    content = data.get("response", {}).get("content", "")
    buttons = data.get("response", {}).get("buttons", [])

    # 创建消息
    msg = cl.Message(content=content)

    # 添加按钮
    for button in buttons:
        msg.actions.append(
            cl.Action(
                name=button.get("action"),
                value=button.get("action"),
                label=button.get("label"),
                payload=button.get("payload", {})
            )
        )

    # 发送消息
    await msg.send()
