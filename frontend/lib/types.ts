export type ArtifactNode = {
  artifactId: string;
  type: string;
  content: string;
  createdBy: string;
  parentArtifactId?: string;
  qualityStatus: string;
  version: number;
};

export type RoleTurn = {
  role: string;
  content: string;
  artifactId?: string;
  timestamp: number;
  decision?: string;
  stage?: string;
  turnType?: "proposal" | "critique" | "challenge" | "revision" | "review" | "feedback" | "execution" | "intent";
  llmBackend?: string;
  llmModel?: string;
  llmError?: string;
  roleReflection?: string;
  roleCorrected?: boolean;
  roleCorrection?: string;
  roleStrategyUpdated?: boolean;
  roleStrategyUpdate?: string;
};

export type ProtocolViewState = {
  allowedRoles: string[];
  decisionRole?: string;
  awaitingDecision: boolean;
  canRevise: boolean;
  activeRole?: string;
  stage?: string;
  round?: number;
  maxRounds?: number;
};

export type ReviewGateState = {
  awaitingDecision: boolean;
  canRevise: boolean;
  decisionRole: string;
  lastDecision?: string;
};

export type SalonEventType =
  | "stage_changed"
  | "round_advanced"
  | "role_turn_started"
  | "role_turn_completed"
  | "role_reflected"
  | "role_corrected"
  | "role_strategy_updated"
  | "artifact_created"
  | "artifact_revised"
  | "review_requested"
  | "review_approved"
  | "review_rejected"
  | "session_paused"
  | "human_intervened";

export type SalonEvent = {
  id: string;
  type: SalonEventType;
  message: string;
  timestamp: number;
};

export type SalonSessionViewState = {
  sessionId: string;
  taskId: string;
  taskTitle: string;
  pattern: string;
  stage: string;
  round: number;
  maxRounds: number;
  activeRole?: string;
  focusArtifactId?: string;
  artifacts: ArtifactNode[];
  turns: RoleTurn[];
  memory: Array<{ memoryId: string; content: string; confidence: number }>;
  protocol: ProtocolViewState;
  reviewGate: ReviewGateState;
  events: SalonEvent[];
  status: string;
};

export type RuntimeState = {
  paused: boolean;
  has_pending: boolean;
  task_count: number;
  memory_count: number;
  updated_at: string;
};

export type SessionListItem = {
  task_id: string;
  goal: string;
  status: string;
  round_index: number;
  artifact_count: number;
  message_count: number;
};
