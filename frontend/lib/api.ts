import { getApiBase, getRoleLlmMap } from "./runtime-settings";
import { mockRuntime } from "./mock-runtime";
import type { RuntimeState, SalonSessionViewState, SessionListItem } from "./types";

type SessionControlAction =
  | "continue_deliberation"
  | "request_review"
  | "enter_revise_path"
  | "pause_session"
  | "human_intervention"
  | "replay_round";

async function request<T>(url: string, init?: RequestInit): Promise<T> {
  const method = init?.method ?? "GET";
  const startedAt = Date.now();
  console.info(`[frontend-api] -> ${method} ${url}`);
  const resp = await fetch(url, init);
  const cost = Date.now() - startedAt;
  console.info(`[frontend-api] <- ${method} ${url} ${resp.status} (${cost}ms)`);
  if (!resp.ok) {
    const text = await resp.text();
    const ct = resp.headers.get("content-type") ?? "";
    if (ct.includes("text/html")) {
      throw new Error(`API endpoint not found (${resp.status}), check apiBase.`);
    }
    throw new Error(text || `HTTP ${resp.status}`);
  }
  return (await resp.json()) as T;
}

function inferTurnType(stage: string, role: string): SalonSessionViewState["turns"][number]["turnType"] {
  if (stage === "proposal") return "proposal";
  if (stage === "deliberation") {
    if (role.includes("critic") || role.includes("challenge")) return "challenge";
    return "critique";
  }
  if (stage === "review") return "review";
  if (stage === "feedback") return "feedback";
  if (stage === "execution") return "execution";
  if (stage === "intent") return "intent";
  return "revision";
}

function mapWorkspaceToView(raw: any): SalonSessionViewState {
  const turns = (raw?.turns ?? []).map((t: any, idx: number) => ({
    role: t.role,
    content: t.content ?? "",
    artifactId: undefined,
    timestamp: Date.parse(t.timestamp ?? "") || Date.now() + idx,
    decision: t.decision ?? "",
    stage: t.stage ?? "",
    turnType: inferTurnType(String(t.stage ?? ""), String(t.role ?? "")),
    llmBackend: t.llm_backend ?? "",
    llmModel: t.llm_model ?? "",
    llmError: t.llm_error ?? "",
    roleReflection: t.role_reflection ?? "",
    roleCorrected: Boolean(t.role_corrected),
    roleCorrection: t.role_correction ?? "",
    roleStrategyUpdated: Boolean(t.role_strategy_updated),
    roleStrategyUpdate: t.role_strategy_update ?? ""
  }));

  const artifacts = (raw?.artifacts ?? []).map((a: any) => ({
    artifactId: a.artifact_id,
    type: a.type,
    content: a.content,
    createdBy: a.created_by,
    parentArtifactId: a.parent_artifact_id ?? undefined,
    qualityStatus: a.quality_status,
    version: a.version
  }));

  const events = (raw?.events ?? []).map((e: any, idx: number) => ({
    id: e.id ?? `evt_${idx}`,
    type: e.type ?? "stage_changed",
    message: e.message ?? "",
    timestamp: Date.parse(e.timestamp ?? "") || Date.now() + idx
  }));

  return {
    sessionId: raw?.session_id ?? "session_unknown",
    taskId: raw?.task_id ?? "",
    taskTitle: raw?.task_title ?? "",
    pattern: raw?.pattern ?? "pattern.unknown",
    stage: raw?.stage ?? "unknown",
    round: raw?.round ?? 1,
    maxRounds: raw?.max_rounds ?? 3,
    activeRole: raw?.active_role ?? undefined,
    focusArtifactId: raw?.focus_artifact_id ?? undefined,
    status: raw?.stage ?? "unknown",
    artifacts,
    turns,
    memory: (raw?.memory ?? []).map((m: any) => ({
      memoryId: m.memory_id,
      content: m.content,
      confidence: m.confidence
    })),
    protocol: {
      allowedRoles: raw?.protocol?.allowed_roles ?? [],
      decisionRole: raw?.review_gate?.decision_role ?? "verifier",
      awaitingDecision: Boolean(raw?.review_gate?.awaiting_decision),
      canRevise: Boolean(raw?.review_gate?.can_revise),
      activeRole: raw?.protocol?.active_role ?? undefined,
      stage: raw?.protocol?.stage ?? undefined,
      round: raw?.protocol?.round ?? undefined,
      maxRounds: raw?.protocol?.max_rounds ?? undefined
    },
    reviewGate: {
      awaitingDecision: Boolean(raw?.review_gate?.awaiting_decision),
      canRevise: Boolean(raw?.review_gate?.can_revise),
      decisionRole: raw?.review_gate?.decision_role ?? "verifier",
      lastDecision: raw?.review_gate?.last_decision ?? undefined
    },
    events
  };
}

export async function fetchRuntimeState(): Promise<{ runtime: RuntimeState; tasks: SessionListItem[] }> {
  const base = getApiBase();
  if (!base) {
    console.info("[frontend-api] MOCK fetchRuntimeState");
    return mockRuntime.getState();
  }
  return request(`${base}/api/state`);
}

export async function fetchSession(taskId: string): Promise<SalonSessionViewState> {
  const base = getApiBase();
  if (!base) {
    console.info(`[frontend-api] MOCK fetchSession task=${taskId}`);
    return mockRuntime.getSession(taskId);
  }
  const raw = await request<any>(`${base}/api/sessions/${encodeURIComponent(taskId)}/workspace`);
  return mapWorkspaceToView(raw);
}

export async function startSalon(goal: string): Promise<{ task_id: string }> {
  const base = getApiBase();
  const roleLlmMap = getRoleLlmMap();
  if (!base) {
    console.info("[frontend-api] MOCK startSalon");
    return mockRuntime.createSession(goal, roleLlmMap);
  }
  return request(`${base}/api/sessions/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      action: "start_salon",
      payload: { goal, auto_run: true, role_llm_map: roleLlmMap }
    })
  });
}

export async function controlSession(taskId: string, action: SessionControlAction, payload?: Record<string, unknown>): Promise<any> {
  const base = getApiBase();
  if (!base) {
    if (action === "continue_deliberation") return mockRuntime.continueSession();
    if (action === "pause_session") return mockRuntime.setPaused(Boolean(payload?.paused));
    if (action === "human_intervention" || action === "enter_revise_path" || action === "request_review") {
      return mockRuntime.continueTask(taskId, String(payload?.note ?? "follow-up"));
    }
    return { ok: true };
  }
  return request(`${base}/api/sessions/${encodeURIComponent(taskId)}/control`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ action, payload: payload ?? {} })
  });
}

export async function pauseSalon(paused: boolean): Promise<{ paused: boolean }> {
  const base = getApiBase();
  if (!base) {
    console.info("[frontend-api] MOCK pauseSalon");
    return mockRuntime.setPaused(paused);
  }
  return request(`${base}/api/runtime/pause`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ paused })
  });
}

export async function continueSalon(): Promise<{ executed: number }> {
  const base = getApiBase();
  if (!base) {
    console.info("[frontend-api] MOCK continueSalon");
    return mockRuntime.continueSession();
  }
  return request(`${base}/api/runtime/continue`, { method: "POST" });
}

export async function followupSalon(taskId: string, input: string): Promise<{ task_id: string }> {
  const base = getApiBase();
  if (!base) {
    console.info(`[frontend-api] MOCK followup task=${taskId}`);
    return mockRuntime.continueTask(taskId, input);
  }
  return request(`${base}/api/tasks/${encodeURIComponent(taskId)}/followup`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ input, auto_run: true })
  });
}
