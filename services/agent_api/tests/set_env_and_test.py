import os
import asyncio
from services.agent_api.services.llm_service import LLMService

async def test_with_env_var():
    """设置环境变量并测试LLMService"""
    print("设置环境变量并测试LLMService...")
    
    # 检查环境变量是否已设置
    api_key = os.environ.get("DASHSCOPE_API_KEY")
    
    if not api_key:
        print("API密钥环境变量未设置")
        return
    
    print("✓ 环境变量已设置")
    
    # 创建LLMService实例
    llm_service = LLMService()
    
    # 测试文本生成
    print("\n测试文本生成...")
    prompt = "请解释什么是机器学习"
    try:
        result = await llm_service.generate(prompt)
        print(f"生成结果: {result[:200]}...")
        print("✓ 文本生成测试通过")
    except Exception as e:
        print(f"✗ 文本生成测试失败: {e}")
    
    # 测试聊天完成
    print("\n测试聊天完成...")
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "请解释什么是机器学习"}
    ]
    try:
        result = await llm_service.chat_completion(messages)
        # 适应阿里云DashScope API的响应格式
        if "output" in result and "text" in result["output"]:
            response_content = result["output"]["text"]
        else:
            response_content = str(result)
        print(f"聊天响应: {response_content[:200]}...")
        print("✓ 聊天完成测试通过")
    except Exception as e:
        print(f"✗ 聊天完成测试失败: {e}")

async def run_test():
    """运行测试"""
    await test_with_env_var()

if __name__ == "__main__":
    asyncio.run(run_test())
