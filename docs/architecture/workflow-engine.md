# Workflow Engine

Workflow Engine 定义任务状态机、阶段门禁与异常恢复策略。

## State Machine

`Intent -> Proposal -> Deliberation -> Execution -> Review -> Feedback`

## Core Rules

- 审议未通过不得进入执行
- 执行失败可重试或回退
- Review 必须输出质量结论
- Feedback 必须沉淀到记忆层
