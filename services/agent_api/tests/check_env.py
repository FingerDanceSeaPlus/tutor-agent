import os

# 检查环境变量
print("检查环境变量...")
dashscope_key = os.getenv("DASHSCOPE_API_KEY")
print(f"DASHSCOPE_API_KEY: {dashscope_key}")

# 检查是否存在
if dashscope_key:
    print("✓ DASHSCOPE_API_KEY 环境变量已设置")
else:
    print("✗ DASHSCOPE_API_KEY 环境变量未设置")

# 检查其他可能的环境变量名称
print("\n检查其他可能的环境变量名称...")
openai_key = os.getenv("OPENAI_API_KEY")
print(f"OPENAI_API_KEY: {openai_key}")

# 打印所有环境变量（可选）
print("\n打印所有环境变量（前20个）...")
env_vars = list(os.environ.items())[:20]
for key, value in env_vars:
    print(f"{key}: {value}")
