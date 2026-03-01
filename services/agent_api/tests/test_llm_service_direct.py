import asyncio
from services.agent_api.services.llm_service import LLMService

async def test_with_api_key():
    """使用手动设置的API密钥测试LLMService"""
    print("使用手动设置的API密钥测试LLMService...")
    
    # 创建LLMService实例
    llm_service = LLMService()
    
    # 手动设置API密钥（请在此处输入您的DASHSCOPE API密钥）
    api_key = ""
    
    if not api_key:
        print("请在代码中设置您的DASHSCOPE API密钥")
        return
    
    # 设置API密钥
    import openai
    openai.api_key = api_key
    
    # 测试文本生成
    print("测试文本生成...")
    prompt = "请解释什么是机器学习"
    try:
        result = await llm_service.generate(prompt)
        print(f"生成结果: {result[:200]}...")
        print("✓ 文本生成测试通过")
    except Exception as e:
        print(f"✗ 文本生成测试失败: {e}")
    
    # 测试聊天完成
    print("测试聊天完成...")
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "请解释什么是机器学习"}
    ]
    try:
        result = await llm_service.chat_completion(messages)
        response_content = result.choices[0].message.content
        print(f"聊天响应: {response_content[:200]}...")
        print("✓ 聊天完成测试通过")
    except Exception as e:
        print(f"✗ 聊天完成测试失败: {e}")

async def run_test():
    """运行测试"""
    await test_with_api_key()

if __name__ == "__main__":
    asyncio.run(run_test())
