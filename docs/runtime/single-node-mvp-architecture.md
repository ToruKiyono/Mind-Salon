# Single Node MVP Architecture

最小可运行形态：单进程/单节点部署，适合原型验证。

## Components

- API Gateway (in-process)
- Scheduler (lightweight)
- Salon Kernel (core)
- Local Store (task/message/artifact/memory)

## Evolution Path

1. 单节点 MVP
2. 组件拆分
3. 多节点与消息总线
4. 分布式运行时
