# 智能编程学习助手

一个基于Chainlit和LangGraph的智能编程学习助手，帮助用户按照一定的流程进行编程学习和刷题。

## 项目结构

```
coach/
├── app.py              # 主应用入口
├── handlers/           # 处理器目录
│   ├── __init__.py
│   ├── action_handler.py  # 动作处理器
│   ├── phase_handler.py   # 阶段处理器
│   └── error_handler.py   # 错误处理器
├── services/           # 服务目录
│   ├── __init__.py
│   ├── state_service.py   # 状态管理服务
│   ├── graph_service.py   # 图处理服务
│   └── problem_service.py # 题目处理服务
├── graphs/             # 图管理目录
│   ├── __init__.py
│   ├── base.py           # 基础图定义
│   ├── subgraphs/        # 子图目录
│   │   ├── __init__.py
│   │   ├── thinking.py    # 思路阶段子图
│   │   ├── coding.py      # 编码阶段子图
│   │   ├── testing.py     # 测试阶段子图
│   │   └── reflecting.py  # 复盘阶段子图
│   └── registry.py        # 图注册和管理
├── utils/              # 工具目录
│   ├── __init__.py
│   ├── action_builder.py  # 动作按钮构建器
│   └── validation.py      # 验证工具
└── schemas/            # 数据模型目录
    └── __init__.py        # 数据模型定义
```

## 核心功能

1. **指导性刷题**：按照思路→编码→测试→复盘的流程进行学习
2. **题目解析**：自动解析题目文本，提取关键信息和测试用例
3. **智能提示**：根据不同阶段提供针对性的提示和建议
4. **测试验证**：运行测试用例验证代码正确性
5. **复盘总结**：提供解题总结和变式题建议

## 技术栈

- Python 3.8+
- Chainlit：用于构建交互式界面
- LangGraph：用于构建和管理状态图
- Pydantic：用于数据验证和模型定义

## 快速开始

### 安装依赖

```bash
pip install -r requirements.txt
```

### 运行应用

```bash
chainlit run app.py
```

## 使用流程

1. **启动应用**：运行 `chainlit run app.py` 启动应用
2. **选择功能**：选择"指导性刷题"功能
3. **设置题目**：粘贴题目原文，系统会自动解析
4. **确认题目**：检查解析结果，确认无误后进入下一阶段
5. **思路阶段**：提交解题思路，可获取提示
6. **编码阶段**：编写代码实现，可运行测试
7. **测试阶段**：运行测试用例，验证代码正确性
8. **复盘阶段**：查看解题总结，可选择做变式题或下一题

## 模块说明

### 服务层
- **StateService**：管理应用状态，提供状态更新和验证
- **GraphService**：管理图的构建和执行
- **ProblemService**：处理题目解析和验证

### 处理器层
- **ActionHandler**：统一处理所有动作回调
- **PhaseHandler**：按阶段处理用户交互
- **ErrorHandler**：集中处理错误

### 图管理
- **BaseGraph**：基础图类
- **SubGraph**：子图类
- **GraphRegistry**：图注册中心

### 工具类
- **ActionBuilder**：构建动作按钮
- **ValidationTool**：验证用户输入和状态

## 扩展指南

### 添加新的子图
1. 在 `graphs/subgraphs/` 目录下创建新的子图文件
2. 继承 `SubGraph` 类并实现 `build` 方法
3. 在 `graphs/__init__.py` 中导出新的子图构建函数
4. 在 `graph.py` 中注册和使用新的子图

### 添加新的动作
1. 在 `ActionHandler` 中注册新的动作回调
2. 在 `PhaseHandler` 中添加相应的处理逻辑
3. 在 `action_builder.py` 中添加动作按钮构建逻辑

## 注意事项

- 题目文本需要包含完整的题目描述和样例输入输出
- 代码实现需要定义 `solve(inp: str) -> str` 函数
- 系统会自动运行测试用例验证代码正确性
- 如遇到问题，可使用"提示"功能获取帮助

## 许可证

MIT
