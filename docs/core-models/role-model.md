# Role Model

Role 定义协作职责边界，同时支持协议约束下的自我纠偏与有界演化。

## Core Fields

- `role_id`
- `role_type`
- `capabilities`
- `authority_scope`
- `context_scope`
- `lifecycle_state`

## RoleProfile

`RoleProfile` 定义角色不可越界的静态约束：

- `responsibilities`: 核心职责
- `bounded_rules`: 不可突破的边界规则
- `allowed_strategy_axes`: 允许调整的策略轴

## RoleAdaptationState

`RoleAdaptationState` 记录有界演化状态：

- `reflection_count`
- `correction_count`
- `strategy_update_count`
- `recurring_issues`
- `strategy_notes`
- `last_reflection`
- `last_correction`
- `last_strategy_update`

## RoleReflection

每次角色回合后可生成 `RoleReflection`：

- `reflection`
- `corrected`
- `correction`
- `strategy_updated`
- `strategy_update`
- `recurring_issue_key`

## Constraints

角色演化必须满足：

- protocol-constrained
- traceable
- memory-informed
- bounded by role responsibility

角色演化不得：

- override protocol authority
- collapse role specialization
- cause uncontrolled personality drift
- freely change core function
