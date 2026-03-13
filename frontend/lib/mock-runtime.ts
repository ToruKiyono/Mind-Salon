import type { RoleLlmMap } from "./runtime-settings";
import type { RuntimeState, SalonSessionViewState, SessionListItem } from "./types";

const STAGE_SEQUENCE = ["intent", "proposal", "deliberation", "execution", "review", "feedback", "done"];
const ROLE_BY_STAGE: Record<string, string> = {
  intent: "planner",
  proposal: "architect",
  deliberation: "reviewer",
  execution: "creator",
  review: "verifier",
  feedback: "coordinator",
  done: "coordinator"
};

function now() {
  return Date.now();
}

function id(prefix: string) {
  return `${prefix}_${Math.random().toString(16).slice(2, 10)}`;
}

class MockRuntime {
  private paused = false;
  private sessions = new Map<string, SalonSessionViewState>();
  private sessionByTask = new Map<string, string>();

  async getState(): Promise<{ runtime: RuntimeState; tasks: SessionListItem[] }> {
    const tasks: SessionListItem[] = [];
    for (const [taskId, sessionId] of this.sessionByTask.entries()) {
      const s = this.sessions.get(sessionId);
      if (!s) continue;
      tasks.push({
        task_id: taskId,
        goal: s.taskTitle,
        status: s.status,
        round_index: s.round,
        artifact_count: s.artifacts.length,
        message_count: s.turns.length
      });
    }
    tasks.sort((a, b) => (a.task_id < b.task_id ? 1 : -1));
    return {
      runtime: {
        paused: this.paused,
        has_pending: false,
        task_count: tasks.length,
        memory_count: tasks.length,
        updated_at: new Date().toISOString()
      },
      tasks
    };
  }

  async getSession(taskId: string): Promise<SalonSessionViewState> {
    const sid = this.sessionByTask.get(taskId);
    if (!sid) throw new Error(`Task not found: ${taskId}`);
    const s = this.sessions.get(sid);
    if (!s) throw new Error(`Session not found: ${sid}`);
    return structuredClone(s);
  }

  async createSession(goal: string, roleLlmMap: RoleLlmMap): Promise<{ task_id: string }> {
    const taskId = id("task");
    const sessionId = id("session");
    const root = id("art");
    const proposal = id("art");
    const final = id("art");
    const ts = now();

    const turns = STAGE_SEQUENCE.filter((s) => s !== "done").map((stage, index) => {
      const role = ROLE_BY_STAGE[stage];
      const model = roleLlmMap[role as keyof RoleLlmMap] ?? "mock/default";
      return {
        role,
        stage,
        decision: stage === "review" ? "pass" : "continue",
        content: `[${role}](${model}) ${stage} on: ${goal}`,
        artifactId: stage === "proposal" ? proposal : stage === "feedback" ? final : undefined,
        timestamp: ts + index * 1000
      };
    });

    const session: SalonSessionViewState = {
      sessionId,
      taskId,
      taskTitle: goal,
      pattern: "pattern.plan_review_execute",
      stage: "done",
      round: 1,
      maxRounds: 3,
      activeRole: "coordinator",
      focusArtifactId: final,
      status: "done",
      artifacts: [
        { artifactId: root, type: "task_root", content: goal, createdBy: "system", qualityStatus: "seeded", version: 1 },
        {
          artifactId: proposal,
          type: "proposal",
          content: "Layered runtime architecture with protocol-aware execution.",
          createdBy: "architect",
          parentArtifactId: root,
          qualityStatus: "generated",
          version: 1
        },
        {
          artifactId: final,
          type: "final",
          content: `final draft for ${goal}`,
          createdBy: "coordinator",
          parentArtifactId: proposal,
          qualityStatus: "approved",
          version: 1
        }
      ],
      turns,
      memory: [{ memoryId: id("mem"), content: `task=${taskId} completed under pattern.plan_review_execute`, confidence: 0.7 }],
      protocol: {
        allowedRoles: ["planner", "architect", "reviewer", "creator", "verifier", "coordinator"],
        decisionRole: "verifier",
        awaitingDecision: false,
        canRevise: true,
        activeRole: "coordinator",
        stage: "done",
        round: 1,
        maxRounds: 3
      },
      reviewGate: {
        awaitingDecision: false,
        canRevise: true,
        decisionRole: "verifier",
        lastDecision: "approve"
      },
      events: [
        { id: id("evt"), type: "stage_changed", message: "Stage moved to proposal", timestamp: ts + 1000 },
        { id: id("evt"), type: "artifact_created", message: "Artifact proposal created", timestamp: ts + 2000 },
        { id: id("evt"), type: "review_requested", message: "Review gate opened", timestamp: ts + 3000 },
        { id: id("evt"), type: "review_approved", message: "Review approved", timestamp: ts + 4000 }
      ]
    };

    this.sessions.set(sessionId, session);
    this.sessionByTask.set(taskId, sessionId);
    return { task_id: taskId };
  }

  async setPaused(paused: boolean): Promise<{ paused: boolean }> {
    this.paused = paused;
    return { paused };
  }

  async continueSession(): Promise<{ executed: number }> {
    return { executed: 0 };
  }

  async continueTask(taskId: string, input: string): Promise<{ task_id: string }> {
    const sid = this.sessionByTask.get(taskId);
    if (!sid) throw new Error(`Task not found: ${taskId}`);
    const s = this.sessions.get(sid);
    if (!s) throw new Error(`Session not found: ${sid}`);

    const ts = now();
    const role = "coordinator";
    s.turns.push({
      role,
      stage: "feedback",
      decision: "continue",
      content: `[${role}] follow-up handled: ${input}`,
      timestamp: ts
    });
    s.events.push({
      id: id("evt"),
      type: "stage_changed",
      message: "follow-up executed",
      timestamp: ts
    });
    s.taskTitle = `${s.taskTitle}\n[follow-up] ${input}`;
    s.status = "done";
    s.round = Math.min(s.round + 1, s.maxRounds);
    s.protocol.round = s.round;
    s.protocol.stage = s.stage;
    s.reviewGate.lastDecision = "continue";
    this.sessions.set(sid, s);
    return { task_id: taskId };
  }
}

export const mockRuntime = new MockRuntime();
