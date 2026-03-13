# Task Model

Task 是系统中的执行单元。

## Fields

- `task_id`
- `title`
- `goal`
- `constraints`
- `status`
- `priority`
- `owner_role`
- `artifacts`

## constraints（常用键）

- `role_llm_map`: `role -> model_id`，直接指定角色模型
- `role_agent_map`: `role -> agent_id | agent_id[] | {"agents": [...], "strategy": ...}`，指定角色 Agent 策略
- `high_risk`: 高风险任务标记（会影响协作调度）

说明：若同时存在多种路由配置，优先级为 `role_llm_map` > `role_agent_map` > `settings.json.role_bindings`。
