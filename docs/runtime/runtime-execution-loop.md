# Runtime Execution Loop

## Loop

```text
Ingress -> Schedule -> Collaborate -> Execute -> Review -> Feedback -> Persist -> Next
```

## Stage Contracts

- 每步必须带 `task_id`
- 每步必须带 `trace_id`
- 状态转换必须可追踪
- 失败路径必须可恢复
