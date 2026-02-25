# 总体介绍
本项目旨在开发一款帮助人入门编程学习的智能agent助手，涵盖从知识检索、学习规划、测验生成、代码测试等一系列新手在编程入门时不可或缺的内容与功能。
# 功能介绍
## 对话功能

是整个程序的入口,支持多轮对话和上下文记忆力功能,同时能对用户的意图进行识别,调用相关的功能模块.

# 架构梳理
## 前端
前端通过chainlit实现
## 推荐的架构
顶层图：TutorAgentGraph

职责：

统一维护 CoachState

决定当前 mode/phase

选择要调用哪个子图

统一处理“中断/等待用户输入”（你现在用按钮驱动）

子图（按功能划分）

对刷题教学专精，合理的子图颗粒度通常是：

ProblemSetupSubgraph：设置题目、解析样例、生成 testcases

ThinkingSubgraph：思路卡引导、判定缺项、提示等级循环

CodingSubgraph：代码规范检查、引导最小修改

TestingSubgraph：运行样例/边界/（可选）随机对拍、失败归因

ReflectSubgraph：复盘卡、变式题、下一题路线

可选增强：

RetrieveSubgraph：知识库检索（为 hint/reflect 提供证据）

VariantTrainingSubgraph：自动生成变式并回到 thinking

你应该如何“切子图”：按工作流边界而不是按按钮

你 UI 的按钮（提交思路/提交代码/运行测试）是触发事件，但子图应该按工作流闭环切分：

“设置题目”不是一颗按钮，而是一段流程：粘贴 → 解析 → 校验 → 生成用例

“提示”不是一颗按钮，而是一段流程：判缺项 → bump level → 输出提示 → 等用户补齐

这样子图内部才能保持高内聚。

1) 子图的接口规范（最关键）

每个子图都应该像一个纯函数（尽量）：

输入：CoachState

输出：更新后的 CoachState

只负责自己那段状态字段（边界清晰）

推荐：每个子图只读/只写的字段约定

例如：

子图	主要读	主要写
ProblemSetup	user input / raw_text	problem.title/testcases/phase
Thinking	attempt.thoughts, hint	phase, ui_message, hint.level
Coding	attempt.code	phase, ui_message
Testing	attempt.code, problem.testcases	evaluation, phase, ui_message
Reflect	evaluation, attempt	artifacts.cheat_sheet, phase

这样顶层图就很容易维护一致性。

4) 顶层路由（Router 节点）怎么写

你顶层图需要一个路由字段（建议叫 mode 或 phase）。

mode：刷题 / 调试 / 讲解（宏观入口）

phase：need_problem / thinking / coding / testing / reflecting（教学阶段）

顶层路由规则（建议）

优先用 phase 决定走哪个子图

mode 决定具体子图版本（例如 debug 子图替换 testing 子图）
