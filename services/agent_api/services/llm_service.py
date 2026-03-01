import asyncio
import os
import requests
from typing import Optional, Dict, Any
import logging

logger = logging.getLogger(__name__)


class LLMService:
    """LLM服务"""
    def __init__(self):
        # 从环境变量读取API密钥
        self.api_key = os.getenv("DASHSCOPE_API_KEY")
        if self.api_key:
            logger.info("DASHSCOPE_API_KEY 环境变量已设置")
        else:
            logger.warning("未设置 DASHSCOPE_API_KEY 环境变量，LLM 服务可能无法正常工作")
        
        self.model = "qwen-turbo"
        self.max_retries = 3
        self.retry_delay = 1.0
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"

    async def generate(self, prompt: str, **kwargs) -> str:
        """生成文本"""
        for attempt in range(self.max_retries):
            try:
                # 检查API密钥是否设置
                if not self.api_key:
                    logger.error("未设置 DASHSCOPE API 密钥，无法调用 API")
                    raise ValueError("未设置 DASHSCOPE API 密钥")
                
                # 构建请求数据
                data = {
                    "model": self.model,
                    "task": "text-generation",
                    "input": {
                        "prompt": prompt
                    },
                    "parameters": {
                        "max_tokens": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7),
                        **kwargs
                    }
                }
                
                # 设置请求头
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 发送请求
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )
                
                # 检查响应状态
                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(f"API请求失败: {e}")
                    logger.error(f"响应内容: {response.text}")
                    raise
                
                # 提取生成的文本
                result = response.json()
                generated_text = result["output"]["text"].strip()
                return generated_text
            except ValueError as e:
                # API密钥错误，不需要重试
                logger.error(f"值错误: {e}")
                raise
            except Exception as e:
                # 其他错误
                logger.error(f"LLM调用失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise

    async def chat_completion(self, messages: list, **kwargs) -> Dict[str, Any]:
        """聊天完成"""
        for attempt in range(self.max_retries):
            try:
                # 检查API密钥是否设置
                if not self.api_key:
                    logger.error("未设置 DASHSCOPE API 密钥，无法调用 API")
                    raise ValueError("未设置 DASHSCOPE API 密钥")
                
                # 构建请求数据
                data = {
                    "model": self.model,
                    "task": "chat-completions",
                    "input": {
                        "messages": messages
                    },
                    "parameters": {
                        "max_tokens": kwargs.get("max_tokens", 1000),
                        "temperature": kwargs.get("temperature", 0.7),
                        **kwargs
                    }
                }
                
                # 设置请求头
                headers = {
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                }
                
                # 发送请求
                # 使用与文本生成相同的API端点
                response = requests.post(
                    self.base_url,
                    headers=headers,
                    json=data
                )
                
                # 检查响应状态
                try:
                    response.raise_for_status()
                except Exception as e:
                    logger.error(f"API请求失败: {e}")
                    logger.error(f"响应内容: {response.text}")
                    raise
                
                # 返回响应
                return response.json()
            except ValueError as e:
                # API密钥错误，不需要重试
                logger.error(f"值错误: {e}")
                raise
            except Exception as e:
                # 其他错误
                logger.error(f"LLM聊天完成失败 (尝试 {attempt+1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                else:
                    raise
