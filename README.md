# Mind Salon v0.2 (Agent Runtime Skeleton)

单机版 Mind Salon v0.2 骨架，覆盖：

- LLM 驱动角色（可插拔 `LLMClient`）
- Tool Calling（注册式 `ToolEngine`）
- Pattern Spec 执行（`PatternExecutor`）
- Memory Retrieval（`MemoryEngine.retrieve`）
- Artifact Tree（父子产物结构）
- 可扩展 Agent Runtime（`AgentRegistry` + `LLMAgent`）

## 环境要求

```bash
python --version  # >= 3.10
```

## 安装与快速运行

```bash
# 方式1：直接运行示例（已处理 src 路径）
python examples/run_mvp.py

# 方式1.1：启动 Mind Salon API（供前端读取 src/mind_salon 运行时）
python examples/run_api_server.py

# 方式1.2：运行前端工作台（Next.js）
cd frontend
npm install
npm run dev

# 方式1.3：一键同时启动后端+前端（推荐本地联调）
# 需要先完成 frontend 目录的 npm install
python examples/run_workspace.py

# 方式2：安装为可编辑包
python -m pip install -e .

# 运行测试
python -m unittest discover -s tests -p 'test_*.py' -q
```

## Frontend（Mind Salon Workspace, Next.js）

先启动 API：

```bash
python examples/run_api_server.py
```

运行：

```bash
cd frontend
npm install
npm run dev
```

也可以直接一键启动（后端+前端）：

```bash
python examples/run_workspace.py
```

打开 `http://127.0.0.1:5173`，可使用以下功能：

- `Start Salon`：提交任务并执行
- `Pause`：暂停自动执行
- `Continue`：执行当前待处理任务
- `Run Next Step`：在当前 Session 上追加 follow-up 指令并继续执行下一轮
- 左侧任务列表：查看 Task 状态与消息/产物计数
- 中央协作区：查看 Stage Timeline 与角色消息
- 右侧面板：查看 Artifacts / Memory / Session 信息

未配置 `apiBase` 时会使用前端内置 Mock Runtime。接入真实后端 API：

```text
http://127.0.0.1:5173?apiBase=http://127.0.0.1:8000
```

## SiliconFlow 接入示例（你给的接口）

项目已内置 `SiliconFlowLLM`：`src/mind_salon/llm/siliconflow.py`

1. 设置环境变量（不要把 Key 写死在代码里）

```bash
# PowerShell
$env:SILICONFLOW_API_KEY="<YOUR_KEY>"
$env:SILICONFLOW_MODEL="Pro/zai-org/GLM-4.7"
```

2. 运行示例

```bash
python examples/run_with_siliconflow.py
```

示例模型优先级：`SILICONFLOW_MODEL` -> `settings.json` 的 `env.ANTHROPIC_MODEL` -> `qwen-plus`。

## settings.json Agent 路由（推荐）

现在支持在 `settings.json` 里声明 LLM Agent 和角色绑定。这样可以同时表达：

- 一个 Agent 服务多个角色（多角色 -> 单 Agent）
- 一个角色配置多个 Agent（单角色 -> 多 Agent，可配置策略）

示例：

```json
{
  "agents": {
    "qwen_main": {
      "provider": "siliconflow",
      "model": "qwen-plus",
      "api_key_env": "SILICONFLOW_API",
      "base_url": "https://dashscope.aliyuncs.com/apps/anthropic",
      "api_style": "anthropic",
      "roles": ["planner", "architect", "critic", "creator", "verifier", "coordinator"]
    },
    "reviewer_backup": {
      "provider": "siliconflow",
      "model": "Pro/zai-org/GLM-4.7",
      "api_key_env": "SILICONFLOW_API",
      "base_url": "https://dashscope.aliyuncs.com/apps/anthropic",
      "api_style": "anthropic"
    }
  },
  "role_bindings": {
    "reviewer": {
      "agents": ["reviewer_backup", "qwen_main"],
      "strategy": "fallback"
    }
  },
  "agent_bindings": {
    "reviewer_backup": ["reviewer"]
  }
}
```

路由优先级：

1. `constraints.role_llm_map`（直接按角色指定模型）
2. `constraints.role_agent_map`（按角色指定 Agent 链）
3. `settings.json.role_bindings`
4. `MindSalonApp` 默认 LLM

`role_bindings[role]` 可写法：

- `["agent_a", "agent_b"]`（默认 `fallback`）
- `{"agents": ["agent_a", "agent_b"], "strategy": "fallback|first|round_robin"}`

你也可以在 `agents.<id>.roles` 或 `agent_bindings` 中反向声明，系统会自动合并到角色策略里。

`api_style` 支持：`auto`（默认）/ `anthropic` / `openai`。  
`auto` 会按 `base_url` 自动判断：
- 包含 `anthropic` 或 `/v1/messages` -> `anthropic`
- 其它 -> `openai`

3. 代码方式注入

```python
from mind_salon import MindSalonApp
from mind_salon.llm import SiliconFlowLLM

llm = SiliconFlowLLM(
    api_key="<YOUR_KEY>",
    model="Pro/zai-org/GLM-4.7",
)
app = MindSalonApp(llm_client=llm)
```

## Key Entry Points

- `src/mind_salon/app.py`: 应用组装与扩展入口
- `src/mind_salon/runtime/execution_loop.py`: Pattern + Agent 执行主循环
- `src/mind_salon/agents/runtime.py`: AgentAction/ToolCall/AgentRegistry
- `src/mind_salon/llm/base.py`: LLM 抽象与 Mock 实现
- `src/mind_salon/llm/siliconflow.py`: SiliconFlow 客户端实现
- `src/mind_salon/kernel/tool_engine.py`: 工具注册与调用
- `src/mind_salon/kernel/memory_engine.py`: 记忆写入与检索
- `src/mind_salon/store/in_memory.py`: Artifact Tree 存储

## 最小使用示例

```python
from mind_salon import MindSalonApp

app = MindSalonApp()  # 默认使用 MockLLM
task_id = app.submit_request("Design a simple runtime execution loop")
results = app.run_until_idle()

print(task_id, results[0].final_status, results[0].artifact_tree)
```

## 自定义 LLM（注册 LLM）

你只需要实现 `LLMClient` 协议中的 `generate` 方法，并在构造 `MindSalonApp` 时注入。

```python
from mind_salon import MindSalonApp
from mind_salon.llm import LLMClient, LLMResponse


class MyLLM(LLMClient):
    def generate(self, *, system_prompt: str, user_prompt: str) -> LLMResponse:
        text = f"[my-llm] {user_prompt[:120]}"
        return LLMResponse(content=text)


app = MindSalonApp(llm_client=MyLLM())
```

## 注册角色 Agent（替换默认角色行为）

默认角色由 `LLMAgent` 提供。你可以注册同名角色覆盖默认实现，或注册新增角色用于新 Pattern。

```python
from mind_salon import MindSalonApp
from mind_salon.agents import BaseAgent, AgentAction, ToolCall


class SeniorReviewerAgent(BaseAgent):
    role_type = "reviewer"

    def act(self, *, context, llm, allow_tool_calls):
        content = "Reviewed with stricter quality gates."
        calls = []
        if allow_tool_calls:
            calls.append(ToolCall(name="generate_result", args={"goal": context.get("goal", "")}))
        return AgentAction(content=content, tool_calls=calls, decision="pass")


app = MindSalonApp()
app.register_agent(SeniorReviewerAgent())
```

## 注册工具（Tool Calling）

注册后，Agent 在 `tool_calls` 中发起的调用会由 `ToolEngine` 执行并回写消息与 Artifact。

```python
from mind_salon import MindSalonApp
from mind_salon.kernel.tool_engine import ToolResult


def search_tool(payload: dict) -> ToolResult:
    query = payload.get("query", "")
    return ToolResult(ok=True, output={"hits": [f"result for {query}"]})


app = MindSalonApp()
app.register_tool("search", search_tool)
```

## 当前支持情况（多角色 / 多模型）

- 多角色：已支持（planner/architect/reviewer/critic/creator/verifier/coordinator）
- 多模型：已支持
  - 方式1：按角色注册不同 Agent 并在 Agent 内调用不同 LLM
  - 方式2：通过 `submit_request(..., constraints={"role_llm_map": {...}})` 动态路由
  - 方式3：通过 `settings.json` 的 `agents + role_bindings` 配置模型 Agent 路由
  - API 模式下可在 `POST /api/tasks` 传入 `role_llm_map` 或 `role_agent_map`
  - Session 续问：`POST /api/tasks/{task_id}/followup`，在同一 task/session 上继续执行

## 扩展点速查

- 自定义 LLM：`MindSalonApp(llm_client=YourLLMClient())`
- 注册/覆盖角色：`app.register_agent(YourAgent())`
- 注册工具：`app.register_tool("tool_name", handler)`
- 调整运行配置：`MindSalonApp(config=SalonConfig(...))`
