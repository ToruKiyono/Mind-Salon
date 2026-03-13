export const ROLE_TYPES = ["planner", "architect", "reviewer", "critic", "creator", "verifier", "coordinator"] as const;
export type RoleType = (typeof ROLE_TYPES)[number];
export type RoleLlmMap = Record<RoleType, string>;

const KEY_API_BASE = "mindSalonApiBase";
const KEY_ROLE_LLM = "mindSalonRoleLlmMap";

export const DEFAULT_ROLE_LLM_MAP: RoleLlmMap = {
  planner: "qwen-plus",
  architect: "qwen-plus",
  reviewer: "qwen-plus",
  critic: "qwen-plus",
  creator: "qwen-plus",
  verifier: "qwen-plus",
  coordinator: "qwen-plus"
};

function isBrowser() {
  return typeof window !== "undefined";
}

function inferLocalApiBase(): string {
  if (!isBrowser()) return "";
  const host = window.location.hostname;
  const isLocal = host === "127.0.0.1" || host === "localhost";
  if (!isLocal) return "";
  return "http://127.0.0.1:8000";
}

export function getApiBase(): string {
  if (!isBrowser()) return "";
  const q = new URLSearchParams(window.location.search).get("apiBase");
  const raw = q ?? window.localStorage.getItem(KEY_API_BASE) ?? inferLocalApiBase();
  return raw.trim().replace(/\/$/, "");
}

export function setApiBase(value: string): string {
  const normalized = value.trim().replace(/\/$/, "");
  if (isBrowser()) {
    if (normalized) window.localStorage.setItem(KEY_API_BASE, normalized);
    else window.localStorage.removeItem(KEY_API_BASE);
  }
  return normalized;
}

export function getRoleLlmMap(): RoleLlmMap {
  if (!isBrowser()) return { ...DEFAULT_ROLE_LLM_MAP };
  const raw = window.localStorage.getItem(KEY_ROLE_LLM);
  if (!raw) return { ...DEFAULT_ROLE_LLM_MAP };
  try {
    const parsed = JSON.parse(raw) as Partial<RoleLlmMap>;
    return {
      planner: parsed.planner || DEFAULT_ROLE_LLM_MAP.planner,
      architect: parsed.architect || DEFAULT_ROLE_LLM_MAP.architect,
      reviewer: parsed.reviewer || DEFAULT_ROLE_LLM_MAP.reviewer,
      critic: parsed.critic || DEFAULT_ROLE_LLM_MAP.critic,
      creator: parsed.creator || DEFAULT_ROLE_LLM_MAP.creator,
      verifier: parsed.verifier || DEFAULT_ROLE_LLM_MAP.verifier,
      coordinator: parsed.coordinator || DEFAULT_ROLE_LLM_MAP.coordinator
    };
  } catch {
    return { ...DEFAULT_ROLE_LLM_MAP };
  }
}

export function setRoleLlmMap(map: RoleLlmMap): void {
  if (!isBrowser()) return;
  window.localStorage.setItem(KEY_ROLE_LLM, JSON.stringify(map));
}
