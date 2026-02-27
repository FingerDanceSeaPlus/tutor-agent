# coach/services/llm_service.py
"""
LLM服务模块
封装LLM调用的逻辑，包括重试机制和缓存机制
"""

from langchain_openai import ChatOpenAI
import os
import time
import hashlib
from typing import Dict, Any, Optional, List

class LLMService:
    """
    LLM服务类
    负责LLM调用的封装，包括重试机制和缓存机制
    """
    
    def __init__(self):
        self.cache = {}
        self.max_retries = 3
        self.retry_delay = 2
    
    def get_llm(self) -> ChatOpenAI:
        """
        获取LLM实例
        """
        return ChatOpenAI(
            api_key=os.getenv("DASHSCOPE_API_KEY"),
            base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
            model="qwen3-max"
        )
    
    def generate_cache_key(self, system_prompt: str, user_input: str) -> str:
        """
        生成缓存键
        """
        combined = f"{system_prompt}|{user_input}"
        return hashlib.md5(combined.encode()).hexdigest()
    
    def invoke_with_retry(self, system_prompt: str, user_input: str) -> str:
        """
        调用LLM，带重试机制
        """
        # 生成缓存键
        cache_key = self.generate_cache_key(system_prompt, user_input)
        
        # 检查缓存
        if cache_key in self.cache:
            return self.cache[cache_key]
        
        # 调用LLM，带重试机制
        for attempt in range(self.max_retries):
            try:
                llm = self.get_llm()
                messages = [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_input}
                ]
                response = llm.invoke(messages)
                output = response.content
                
                # 缓存结果
                self.cache[cache_key] = output
                return output
            except Exception as e:
                print(f"LLM调用失败 (尝试 {attempt + 1}/{self.max_retries}): {e}")
                if attempt < self.max_retries - 1:
                    time.sleep(self.retry_delay)
                else:
                    raise
    
    def clear_cache(self):
        """
        清除缓存
        """
        self.cache.clear()
    
    def get_cache_size(self) -> int:
        """
        获取缓存大小
        """
        return len(self.cache)
