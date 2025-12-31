from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
import os
from langchain.agents import create_agent
chatLLM = ChatOpenAI(
    api_key=os.getenv("DASHSCOPE_API_KEY"),
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen-plus",  # 此处以qwen-plus为例，您可按需更换模型名称。模型列表：https://help.aliyun.com/zh/model-studio/getting-started/models
    # other params...
)


def build_agent(llm: ChatOpenAI):
    agent=create_agent(
        model=llm,
        checkpointer=InMemorySaver(),
    )
    return agent




def chat_node(input_data: str) -> str:
    agent = build_agent(chatLLM)
    response = agent.invoke({"input": input_data})
    print(response['output'])