import os
import json
from langchain_openai import ChatOpenAI

# 检查环境变量
api_key = os.getenv("DASHSCOPE_API_KEY")
print(f"API key exists: {api_key is not None}")

# 构建system prompt和user input
system_prompt = "你是一个专业的编程题目分析助手，擅长提取题目信息并结构化。请根据用户提供的指令分析题目并返回结构化结果。"

problem_text = '''题目：两数之和
给定一个整数数组 nums 和一个目标值 target，请你在该数组中找出和为目标值的那两个整数，并返回它们的数组下标。
你可以假设每种输入只会对应一个答案。但是，数组中同一个元素不能使用两遍。
示例：
输入：nums = [2, 7, 11, 15], target = 9
输出：[0, 1]
解释：因为 nums[0] + nums[1] = 2 + 7 = 9，所以返回 [0, 1]。
约束条件：
- 2 <= nums.length <= 10^4
- -10^9 <= nums[i] <= 10^9
- -10^9 <= target <= 10^9
- 只会存在一个有效答案'''

user_input = '''
请分析以下编程题目，提取并结构化以下信息：

1. 标题：题目的简短标题
2. 描述：题目主体描述，去除标题、约束、样例等部分
3. 约束条件：题目中的约束条件
4. 样例：输入输出对，格式为[["input": "...", "expected": "..."]]
5. 标签：题目相关的算法标签
6. 难度：估计题目难度（简单/中等/困难）

题目文本：
{problem_text}

请只返回JSON格式的结果，不要包含其他任何文本，包含上述所有字段。
'''.format(problem_text=problem_text)

# 修复格式字符串中的大括号
user_input = user_input.replace('[[', '{').replace(']]', '}')

print(f"User input: {user_input[:100]}...")

# 调用LLM - 直接使用ChatOpenAI实例
llm = ChatOpenAI(
    api_key=api_key,
    base_url="https://dashscope.aliyuncs.com/compatible-mode/v1",
    model="qwen3-max"
)

# 构建消息
messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": user_input}
]

# 调用LLM
print("Calling LLM...")
try:
    response = llm.invoke(messages)
    agent_output = response.content
    print(f"LLM output: {agent_output}")
    
    # 写入到文件以便查看完整输出
    with open("llm_output.txt", "w", encoding="utf-8") as f:
        f.write(agent_output)
    print("Output written to llm_output.txt")
    
    # 解析结果
    try:
        extraction_result = json.loads(agent_output)
        print(f"Extraction result: {extraction_result}")
    except Exception as e:
        print(f"Error parsing JSON: {e}")
        # 尝试从输出中提取JSON部分
        import re
        # 尝试匹配完整的JSON对象，包括嵌套的
        json_match = re.search(r'\{[\s\S]*\}', agent_output)
        if json_match:
            json_str = json_match.group(0)
            print(f"Extracted JSON string: {json_str}")
            try:
                extraction_result = json.loads(json_str)
                print(f"Extracted JSON: {extraction_result}")
            except Exception as e2:
                print(f"Error parsing extracted JSON: {e2}")
                # 尝试清理JSON字符串
                json_str = json_str.replace('\\n', '').replace('\\t', '')
                print(f"Cleaned JSON string: {json_str}")
                try:
                    extraction_result = json.loads(json_str)
                    print(f"Cleaned JSON: {extraction_result}")
                except Exception as e3:
                    print(f"Error parsing cleaned JSON: {e3}")
        else:
            print("No JSON found in output")
except Exception as e:
    print(f"Error calling LLM: {e}")
    import traceback
    traceback.print_exc()