import asyncio
import os
from services.agent_api.services.llm_service import LLMService

async def test_generate():
    """测试文本生成功能"""
    print("测试文本生成功能...")
    
    # 创建LLMService实例
    llm_service = LLMService()
    
    # 测试提示词
    prompt = "请解释什么是机器学习"
    
    try:
        # 调用generate方法
        result = await llm_service.generate(prompt)
        print(f"生成结果: {result[:100]}...")
        print("✓ 文本生成测试通过")
    except Exception as e:
        print(f"✗ 文本生成测试失败: {e}")

async def test_chat_completion():
    """测试聊天完成功能"""
    print("测试聊天完成功能...")
    
    # 创建LLMService实例
    llm_service = LLMService()
    
    # 测试消息
    messages = [
        {"role": "system", "content": "你是一个助手"},
        {"role": "user", "content": "请解释什么是机器学习"}
    ]
    
    try:
        # 调用chat_completion方法
        result = await llm_service.chat_completion(messages)
        response_content = result.choices[0].message.content
        print(f"聊天响应: {response_content[:100]}...")
        print("✓ 聊天完成测试通过")
    except Exception as e:
        print(f"✗ 聊天完成测试失败: {e}")

async def test_api_key_missing():
    """测试API密钥缺失的情况"""
    print("测试API密钥缺失的情况...")
    
    # 保存原始API密钥
    original_api_key = os.environ.get("OPENAI_API_KEY")
    
    try:
        # 删除API密钥
        if "OPENAI_API_KEY" in os.environ:
            del os.environ["OPENAI_API_KEY"]
        
        # 创建LLMService实例
        llm_service = LLMService()
        
        # 测试生成功能
        prompt = "请解释什么是机器学习"
        try:
            await llm_service.generate(prompt)
            print("✗ API密钥缺失测试失败: 应该抛出异常")
        except ValueError as e:
            print(f"✓ API密钥缺失测试通过: {e}")
    finally:
        # 恢复原始API密钥
        if original_api_key:
            os.environ["OPENAI_API_KEY"] = original_api_key

async def run_all_tests():
    """运行所有测试"""
    print("开始测试LLMService功能...")
    
    await test_generate()
    await test_chat_completion()
    await test_api_key_missing()
    
    print("\n🎉 所有测试完成！")

if __name__ == "__main__":
    asyncio.run(run_all_tests())
