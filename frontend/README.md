# Mind Salon Frontend

基于 `docs/ui` 重新生成，核心遵循：

- Session-first
- Protocol-aware
- Artifact-centered
- Round-visible

## 技术栈

- Next.js (App Router)
- React + TypeScript
- Tailwind CSS
- TanStack Query
- Zustand

## 运行

```bash
cd frontend
npm install
npm run dev
```

打开：`http://127.0.0.1:5173`

## Runtime 对接

- 启动后端 API（在仓库根目录）：

```bash
python examples/run_api_server.py
```

- 推荐在页面底部 `Runtime Endpoint` 输入 `apiBase` 并点击 `Apply`
- 也可通过 URL：`?apiBase=http://127.0.0.1:8000`

未配置 `apiBase` 时使用内置 Mock Runtime。

## 主要视图组件

- Session Navigation
- ProtocolRail
- FocusManuscript
- RoleTurnStream
- ArtifactThread
- MemoryAside
- ReviewGate
- InterventionBar (collaboration actions)

## Inspector / Settings (collapsed by default)

`Runtime Endpoint`、`Role LLM Routing`、`Low-level Runtime Controls`、`Event Stream` 均位于折叠面板中，默认工作台不展示基础设施配置。
