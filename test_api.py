import httpx
import json

# 测试创建会话
async def test_create_session():
    async with httpx.AsyncClient() as client:
        response = await client.post("http://localhost:8002/sessions", json={})
        print(f"创建会话响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"会话ID: {data.get('session_id')}")
            return data.get('session_id')
        return None

# 测试发送消息
async def test_send_message(session_id):
    async with httpx.AsyncClient() as client:
        payload = {
            "session_id": session_id,
            "event": {
                "type": "TEXT",
                "payload": {
                    "content": "测试消息"
                }
            }
        }
        response = await client.post("http://localhost:8002/events", json=payload)
        print(f"发送消息响应: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"响应内容: {data}")
        else:
            print(f"错误信息: {response.text}")

# 主函数
async def main():
    # 创建会话
    session_id = await test_create_session()
    if session_id:
        # 发送消息
        await test_send_message(session_id)

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())