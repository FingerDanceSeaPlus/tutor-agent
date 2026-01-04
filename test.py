from langchain_openai import ChatOpenAI

from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langgraph.checkpoint.memory import InMemorySaver
from langchain_core.runnables import Runnable, RunnableConfig, RunnableLambda
from typing import cast

import chainlit as cl
from chains .chat import build_agent
import os


def extract_agent_output(agent_output):
    """从agent输出中提取纯文本，类似StrOutputParser"""
    if isinstance(agent_output, dict) and "messages" in agent_output:
        messages = agent_output["messages"]
        if messages:
            last_message = messages[-1]
            return last_message.content if hasattr(last_message, "content") else str(last_message)
    return str(agent_output)


@cl.on_chat_start
async def on_chat_start():
    chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
    )
    
    
    # 使用 RunnableLambda 包装解析函数，类似 StrOutputParser
    output_parser = StrOutputParser()
    agent = build_agent(chatLLM)
    runnable = agent | output_parser
    cl.user_session.set("runnable", runnable)


@cl.on_message
async def on_message(message: cl.Message):
    runnable = cast(Runnable, cl.user_session.get("runnable"))  # type: Runnable

    msg = cl.Message(content="")

    async for chunk in runnable.astream(
        {"messages": [("user", message.content)]},
        config=RunnableConfig(callbacks=[cl.LangchainCallbackHandler()], configurable={"thread_id": "1"}),
    ):
        await msg.stream_token(chunk)

    await msg.send()