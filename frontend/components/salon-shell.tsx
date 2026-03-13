"use client";

import { AnimatePresence, motion } from "framer-motion";
import { useEffect, useMemo, useRef, useState } from "react";
import { type TFunction } from "i18next";
import { useTranslation } from "react-i18next";
import { useActions, useRuntime, useSession } from "@/hooks/use-salon";
import { DEFAULT_ROLE_LLM_MAP, ROLE_TYPES, type RoleLlmMap, getApiBase, getRoleLlmMap, setApiBase, setRoleLlmMap } from "@/lib/runtime-settings";
import type { ArtifactNode, RoleTurn, SalonEvent } from "@/lib/types";
import { useUiStore } from "@/store/ui-store";
import { LanguageSwitcher } from "./language-switcher";
import { ThemeSwitcher } from "./theme-switcher";

const CAST_ORDER = ["planner", "architect", "critic", "challenger", "reviewer"] as const;
const STAGES = ["intent", "proposal", "deliberation", "execution", "review", "feedback", "done"] as const;
const ROLE_STYLES: Record<string, { accent: string; tint: string; avatar: string }> = {
  planner: { accent: "255 156 212", tint: "255 237 248", avatar: "AI" },
  architect: { accent: "102 184 255", tint: "231 245 255", avatar: "EG" },
  critic: { accent: "120 176 155", tint: "233 244 239", avatar: "CS" },
  challenger: { accent: "255 114 126", tint: "255 236 240", avatar: "AS" },
  reviewer: { accent: "183 141 255", tint: "243 236 255", avatar: "JG" },
  creator: { accent: "80 207 255", tint: "228 248 255", avatar: "CR" },
  verifier: { accent: "210 170 91", tint: "251 245 228", avatar: "VF" },
  coordinator: { accent: "255 122 196", tint: "255 237 247", avatar: "CO" }
};
const shellMotion = { hidden: { opacity: 0, y: 22 }, visible: { opacity: 1, y: 0, transition: { duration: 0.45 } } };
const bubbleMotion = {
  hidden: { opacity: 0, y: 28, scale: 0.96 },
  visible: (index: number) => ({ opacity: 1, y: 0, scale: 1, transition: { duration: 0.38, delay: index * 0.08 } }),
  exit: { opacity: 0, y: -12, scale: 0.98, transition: { duration: 0.2 } }
};

function roleStyle(role: string) {
  return ROLE_STYLES[role] ?? { accent: "143 166 201", tint: "238 243 250", avatar: role.slice(0, 2).toUpperCase() };
}
function roleCopy(role: string, t: TFunction) {
  const value = t(`roles.${role}`, { returnObjects: true }) as Record<string, string> | string;
  if (!value || typeof value === "string") return { badge: role, persona: t("roles.fallback.persona"), title: t("roles.fallback.title") };
  return { badge: value.badge ?? role, persona: value.persona ?? t("roles.fallback.persona"), title: value.title ?? t("roles.fallback.title") };
}
function formatTime(language: string, t: TFunction, timestamp?: number) {
  if (!timestamp) return t("app.noTimestamp");
  return new Intl.DateTimeFormat(language === "zh" ? "zh-CN" : "en-US", { hour: "2-digit", minute: "2-digit", month: "short", day: "numeric" }).format(new Date(timestamp));
}
function translateStatus(status: string, t: TFunction) { return t(`status.${status}`, { defaultValue: status }); }
function translateEventType(type: string, t: TFunction) { return t(`events.types.${type}`, { defaultValue: type }); }
function stageLabel(stage: string | undefined, t: TFunction) { return stage ? t(`stage.stages.${stage}`, { defaultValue: stage }) : t("stage.awaitingRole"); }
function roleLabel(role: string | undefined, t: TFunction) { return role ? roleCopy(role, t).badge : t("stage.awaitingRole"); }
function actionButtonClass(primary = false) {
  return primary
    ? "salon-button rounded-[999px] border border-salon-primary/35 bg-[linear-gradient(135deg,rgb(var(--salon-primary)/0.96),rgb(var(--salon-accent)/0.82))] px-5 py-3 text-sm font-semibold text-white shadow-float disabled:cursor-not-allowed disabled:opacity-60"
    : "salon-button rounded-[999px] border border-salon-line/70 bg-salon-panel/55 px-5 py-3 text-sm text-salon-text shadow-soft disabled:cursor-not-allowed disabled:opacity-60";
}
function lineageDepth(artifact: ArtifactNode, byId: Map<string, ArtifactNode>) {
  let depth = 0;
  let current = artifact.parentArtifactId ? byId.get(artifact.parentArtifactId) : undefined;
  while (current) { depth += 1; current = current.parentArtifactId ? byId.get(current.parentArtifactId) : undefined; }
  return depth;
}
function splitContent(content: string) {
  const paragraphs = content.split(/\n+/).map((item) => item.trim()).filter(Boolean);
  if (paragraphs.length >= 2) return paragraphs;
  return content.split(/(?<=[.!?。！？])\s+/).map((item) => item.trim()).filter(Boolean);
}
function thoughtBlocks(turn: RoleTurn, t: TFunction) {
  const segments = splitContent(turn.content);
  return [
    { key: "idea", content: segments[0] ?? turn.content },
    { key: "structure", content: segments.slice(1).join(" ") || (turn.stage ? t(`stage.stageDescriptions.${turn.stage}`, { defaultValue: t("chat.turnFallback") }) : t("chat.turnFallback")) },
    { key: "artifact", content: turn.artifactId ? `${t("stage.artifact")} ${turn.artifactId}` : t("chat.noArtifactRef") },
    { key: "reflection", content: turn.roleReflection ?? turn.roleCorrection ?? turn.roleStrategyUpdate ?? t("app.none") }
  ];
}
function FloatingTag({ label, value }: { label: string; value: string }) {
  return <div className="salon-floating-chip"><span className="text-[10px] uppercase tracking-[0.32em] text-salon-sub">{label}</span><span className="text-sm font-semibold text-salon-text">{value}</span></div>;
}

function SalonHeader({ paused, usingMockSource, taskCount, memoryCount, sessionId }: { paused: boolean; usingMockSource: boolean; taskCount: number; memoryCount: number; sessionId?: string }) {
  const { t } = useTranslation();
  return (
    <motion.header className="salon-hero-shell" variants={shellMotion} initial="hidden" animate="visible">
      <div className="flex flex-col gap-5 xl:flex-row xl:items-center xl:justify-between">
        <div className="flex items-start gap-4">
          <div className="salon-logo-mark"><span>MS</span></div>
          <div className="max-w-3xl">
            <div className="text-[11px] uppercase tracking-[0.42em] text-salon-sub">{t("app.theatre")}</div>
            <h1 className="salon-display mt-3 text-5xl font-semibold tracking-tight text-salon-text sm:text-6xl">{t("app.brand")}</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-salon-sub sm:text-base">{t("header.heroBody")}</p>
          </div>
        </div>
        <div className="grid gap-3 sm:grid-cols-2 xl:w-[440px]">
          <div className="sm:col-span-2 flex gap-3"><LanguageSwitcher /></div>
          <FloatingTag label={t("header.runtime")} value={paused ? t("header.paused") : t("app.live")} />
          <FloatingTag label={t("header.source")} value={usingMockSource ? t("header.mock") : t("header.remote")} />
          <FloatingTag label={t("header.tasks")} value={String(taskCount)} />
          <FloatingTag label={t("header.memory")} value={String(memoryCount)} />
          <div className="salon-floating-chip sm:col-span-2"><span className="text-[10px] uppercase tracking-[0.32em] text-salon-sub">{t("header.session")}</span><span className="truncate text-sm font-semibold text-salon-text">{sessionId ?? t("header.noSession")}</span></div>
        </div>
      </div>
    </motion.header>
  );
}

function SessionNavigation({ selectedTaskId, setSelectedTaskId, tasks }: { selectedTaskId: string | null; setSelectedTaskId: (taskId: string) => void; tasks: Array<{ task_id: string; goal: string; status: string; round_index: number; message_count: number }> }) {
  const { t } = useTranslation();
  return (
    <motion.aside className="salon-floating-surface px-4 py-5" variants={shellMotion} initial="hidden" animate="visible">
      <div className="mb-5 flex items-center justify-between"><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("sessionAtlas.title")}</div><h2 className="salon-display mt-2 text-2xl text-salon-text">{t("sessionAtlas.subtitle")}</h2></div><span className="rounded-full bg-salon-panel/55 px-3 py-1 text-xs text-salon-sub">{tasks.length}</span></div>
      <div className="grid gap-3">
        {!tasks.length ? <div className="salon-whisper-panel text-sm text-salon-sub">{t("sessionAtlas.empty")}</div> : null}
        {tasks.map((task, index) => { const active = task.task_id === selectedTaskId; return <motion.button key={task.task_id} type="button" layout onClick={() => setSelectedTaskId(task.task_id)} className={`salon-session-pill ${active ? "is-active" : ""}`} whileHover={{ y: -4 }} whileTap={{ scale: 0.99 }}><div className="flex items-start gap-3"><span className="salon-orb inline-flex h-12 w-12 shrink-0 items-center justify-center rounded-[18px] text-sm font-semibold text-white">{String(index + 1).padStart(2, "0")}</span><div className="min-w-0 flex-1 text-left"><div className="truncate text-sm font-semibold text-salon-text">{task.goal}</div><div className="mt-1 text-[11px] uppercase tracking-[0.22em] text-salon-sub">{task.task_id}</div></div></div><div className="mt-3 flex items-center justify-between gap-2 text-xs text-salon-sub"><span className="salon-mini-badge">{translateStatus(task.status, t)}</span><span>{t("app.round")} {task.round_index}</span><span>{task.message_count} {t("sessionAtlas.turns")}</span></div></motion.button>; })}
      </div>
      <div className="mt-5"><div className="mb-3 text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("theme.title")}</div><ThemeSwitcher /></div>
    </motion.aside>
  );
}
function RoleEnsemble({ activeRole }: { activeRole?: string }) {
  const { t } = useTranslation();
  return <div className="salon-cast-ensemble">{CAST_ORDER.map((role, index) => { const style = roleStyle(role); const copy = roleCopy(role, t); const active = role === activeRole; return <motion.div key={role} className={`salon-cast-actor slot-${index + 1} ${active ? "is-active" : ""}`} style={{ borderColor: `rgb(${style.accent} / 0.3)` }} initial={{ opacity: 0, y: 18, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: active ? 1.05 : 1 }} transition={{ delay: index * 0.06 }}><motion.div className="salon-role-avatar salon-cast-avatar" style={{ background: `linear-gradient(135deg, rgb(${style.accent}), rgb(var(--salon-accent) / 1))` }} animate={active ? { boxShadow: [`0 0 0 rgba(0,0,0,0)`, `0 0 30px rgb(${style.accent} / 0.45)`, `0 0 0 rgba(0,0,0,0)`] } : undefined} transition={{ duration: 2, repeat: Infinity }}>{style.avatar}</motion.div><div className="salon-cast-copy"><div className="salon-cast-name">{copy.badge}</div><div className="salon-cast-persona">{copy.persona}</div></div></motion.div>; })}</div>;
}

function FocusManuscript({ artifact, stage, round, maxRounds, isBusy }: { artifact?: ArtifactNode; stage?: string; round?: number; maxRounds?: number; isBusy: boolean }) {
  const { t } = useTranslation();
  return <motion.section className="salon-manuscript-shell" layout variants={shellMotion} initial="hidden" animate="visible"><div className="salon-manuscript-header"><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("stage.focusManuscript")}</div><h3 className="salon-display mt-2 text-2xl text-salon-text">{artifact ? artifact.type : t("stage.awaitingArtifact")}</h3></div><div className="flex flex-wrap gap-2"><span className="salon-mini-badge">{stageLabel(stage, t)}</span><span className="salon-mini-badge">{t("app.round")} {round ?? 0}/{maxRounds ?? 0}</span><span className="salon-mini-badge">{isBusy ? t("app.live") : t("stage.resting")}</span></div></div>{!artifact ? <div className="salon-manuscript-empty">{t("stage.noFocusArtifactYet")}</div> : <motion.div key={`${artifact.artifactId}-${artifact.version}`} layoutId={`artifact-${artifact.artifactId}`} className="salon-manuscript-paper" initial={{ opacity: 0, y: 18, scale: 0.98 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.4 }}><div className="mb-5 flex flex-wrap items-center justify-between gap-3"><div className="flex items-center gap-3"><span className="salon-orb inline-flex h-14 w-14 items-center justify-center rounded-[22px] text-sm font-semibold uppercase text-white">{artifact.type.slice(0, 2)}</span><div><div className="text-[10px] uppercase tracking-[0.34em] text-salon-sub">{t("stage.currentArtifact")}</div><div className="text-lg font-semibold text-salon-text">{artifact.artifactId}</div></div></div><div className="flex flex-wrap gap-2"><span className="salon-version-pill">v{artifact.version}</span><span className="salon-revision-pill">{artifact.qualityStatus}</span></div></div><p className="text-sm leading-8 text-salon-text sm:text-[15px]">{artifact.content}</p><div className="salon-manuscript-meta mt-5"><FloatingTag label={t("stage.createdBy")} value={artifact.createdBy} /><FloatingTag label={t("stage.parent")} value={artifact.parentArtifactId ?? t("stage.root")} /><FloatingTag label={t("stage.artifact")} value={artifact.artifactId} /></div></motion.div>}</motion.section>;
}

function ProtocolPath({ stage }: { stage?: string }) {
  const { t } = useTranslation();
  return <div className="salon-protocol-strip"><div className="text-[10px] uppercase tracking-[0.3em] text-salon-sub">{t("stage.stageTransition")}</div><div className="mt-2 flex flex-wrap gap-2">{STAGES.map((item, index) => <motion.div key={item} className={`salon-stage-chip ${item === stage ? "is-active" : ""}`} initial={{ opacity: 0, x: -12 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.04 }}>{t(`stage.stages.${item}`)}</motion.div>)}</div></div>;
}

function ChatMessage({ turn, index, running, shouldAnimateIn, language }: { turn: RoleTurn; index: number; running: boolean; shouldAnimateIn: boolean; language: string }) {
  const { t } = useTranslation();
  const style = roleStyle(turn.role);
  const copy = roleCopy(turn.role, t);
  const blocks = thoughtBlocks(turn, t);
  const isRight = index % 2 === 1;
  return <motion.article custom={index} variants={bubbleMotion} initial={shouldAnimateIn ? "hidden" : false} animate="visible" exit="exit" layout className={`salon-chat-message ${isRight ? "is-right" : ""}`}><div className="salon-chat-avatar-wrap"><motion.div className="salon-role-avatar salon-chat-avatar" style={{ background: `linear-gradient(135deg, rgb(${style.accent}), rgb(var(--salon-accent) / 1))` }} animate={running ? { boxShadow: [`0 0 0 rgba(0,0,0,0)`, `0 0 24px rgb(${style.accent} / 0.36)`, `0 0 0 rgba(0,0,0,0)`] } : undefined} transition={running ? { duration: 2.4, repeat: Infinity } : undefined}>{style.avatar}</motion.div></div><div className="salon-chat-body"><div className="salon-chat-meta"><div className="flex flex-wrap items-center gap-2"><span className="salon-role-badge" style={{ backgroundColor: `rgb(${style.accent} / 0.14)`, color: `rgb(${style.accent})` }}>{copy.badge}</span><span className="salon-mini-badge">{copy.persona}</span><span className="salon-chat-title">{copy.title}</span></div><div className="text-xs text-salon-sub">{formatTime(language, t, turn.timestamp)}</div></div><div className="salon-chat-bubble" style={{ borderColor: `rgb(${style.accent} / 0.25)`, background: `linear-gradient(180deg, rgb(var(--salon-panel) / 0.9), rgb(${style.tint} / 0.94))` }}><div className="grid gap-3">{blocks.map((block, blockIndex) => <motion.div key={`${turn.timestamp}-${block.key}`} className="salon-note-shard" initial={shouldAnimateIn ? { opacity: 0, y: 10 } : false} animate={{ opacity: 1, y: 0 }} transition={{ delay: blockIndex * 0.08, duration: 0.25 }}><div className="text-[10px] uppercase tracking-[0.2em] text-salon-sub">{t(`chat.blocks.${block.key}`)}</div><div className="mt-1 text-sm leading-7 text-salon-text">{block.content}</div></motion.div>)}</div><div className="mt-4 flex flex-wrap gap-2 text-xs"><span className="salon-mini-badge">{turn.turnType ? t(`chat.turnTypes.${turn.turnType}`, { defaultValue: turn.turnType }) : turn.stage ? stageLabel(turn.stage, t) : t("chat.turnFallback")}</span><span className="salon-mini-badge">{turn.decision ?? t("chat.noDecision")}</span><span className="salon-mini-badge">{turn.artifactId ? `${t("stage.artifact")} ${turn.artifactId}` : t("chat.noArtifactRef")}</span><span className="salon-mini-badge">{turn.llmModel ?? t("chat.modelPending")}</span></div>{running ? <motion.div className="salon-live-trace" initial={{ scaleX: 0 }} animate={{ scaleX: 1 }} transition={{ duration: 1.6, repeat: Infinity }} /> : null}{turn.llmError ? <div className="mt-4 rounded-[24px] bg-salon-danger/12 px-4 py-3 text-sm text-salon-text">{turn.llmError}</div> : null}</div></div></motion.article>;
}

function ChatTimeline({ turns, totalTurns, activeRole, language }: { turns: RoleTurn[]; totalTurns: number; activeRole?: string; language: string }) {
  const { t } = useTranslation();
  const previousCount = useRef(0);
  const enteringStartIndex = useRef(0);
  useEffect(() => { enteringStartIndex.current = turns.length > previousCount.current ? previousCount.current : turns.length; previousCount.current = turns.length; }, [turns.length]);
  return <section className="salon-chat-shell"><div className="mb-5 flex flex-wrap items-end justify-between gap-3"><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("chat.title")}</div><h3 className="salon-display mt-2 text-2xl text-salon-text">{t("chat.subtitle")}</h3></div><div className="flex flex-wrap gap-2"><span className="salon-mini-badge">{roleLabel(activeRole, t)}</span><span className="salon-mini-badge">{turns.length} / {totalTurns} {t("app.visible")}</span></div></div>{!turns.length ? <div className="salon-whisper-panel text-sm text-salon-sub">{t("chat.empty")}</div> : null}<div className="salon-chat-timeline"><AnimatePresence mode="popLayout">{turns.map((turn, index) => <ChatMessage key={`${turn.role}-${turn.timestamp}-${index}`} turn={turn} index={index} running={index === turns.length - 1 && turns.length < totalTurns} shouldAnimateIn={index >= enteringStartIndex.current} language={language} />)}</AnimatePresence></div></section>;
}

function ArtifactLab({ artifacts }: { artifacts: ArtifactNode[] }) {
  const { t } = useTranslation();
  const byId = useMemo(() => new Map(artifacts.map((artifact) => [artifact.artifactId, artifact])), [artifacts]);
  return <motion.section className="salon-floating-surface px-4 py-5" variants={shellMotion} initial="hidden" animate="visible"><div className="mb-5"><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("artifactLab.title")}</div><h3 className="salon-display mt-2 text-2xl text-salon-text">{t("artifactLab.subtitle")}</h3></div><div className="grid gap-3">{!artifacts.length ? <div className="salon-whisper-panel text-sm text-salon-sub">{t("artifactLab.empty")}</div> : null}{artifacts.map((artifact, index) => { const depth = lineageDepth(artifact, byId); return <motion.article key={`${artifact.artifactId}-${artifact.version}`} layout layoutId={`artifact-${artifact.artifactId}`} className="salon-artifact-object" style={{ marginLeft: `${depth * 14}px` }} initial={{ opacity: 0, y: 18, scale: 0.95 }} animate={{ opacity: 1, y: 0, scale: 1 }} transition={{ duration: 0.35, delay: index * 0.04 }}><div className="flex items-start justify-between gap-3"><div><div className="text-[10px] uppercase tracking-[0.26em] text-salon-sub">{artifact.type}</div><div className="mt-1 text-sm font-semibold text-salon-text">{artifact.artifactId}</div><div className="mt-1 text-xs text-salon-sub">{t("artifactLab.by")} {artifact.createdBy}</div></div><div className="flex flex-wrap gap-2"><span className="salon-version-pill">v{artifact.version}</span><span className="salon-revision-pill">{artifact.qualityStatus}</span></div></div><div className="mt-3 text-sm leading-6 text-salon-text">{artifact.content}</div><div className="mt-3 flex flex-wrap gap-2 text-xs text-salon-sub"><span>{artifact.parentArtifactId ? `${t("stage.parent")} ${artifact.parentArtifactId}` : t("artifactLab.rootObject")}</span><span>{depth > 0 ? `${t("artifactLab.revisionBranch")} ${depth}` : t("artifactLab.originNode")}</span></div></motion.article>; })}</div></motion.section>;
}
function MemoryPanel({ memory }: { memory: Array<{ memoryId: string; content: string; confidence: number }> }) {
  const { t } = useTranslation();
  return <motion.section className="salon-floating-surface px-4 py-5" variants={shellMotion} initial="hidden" animate="visible"><div className="mb-5"><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("memoryPanel.title")}</div><h3 className="salon-display mt-2 text-2xl text-salon-text">{t("memoryPanel.subtitle")}</h3></div><div className="grid gap-3">{!memory.length ? <div className="salon-whisper-panel text-sm text-salon-sub">{t("memoryPanel.empty")}</div> : null}{memory.map((item, index) => <motion.article key={item.memoryId} className="salon-memory-star" initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: index * 0.05 }}><div className="flex items-center justify-between gap-2"><div className="text-xs font-semibold uppercase tracking-[0.22em] text-salon-sub">{item.memoryId}</div><span className="salon-mini-badge">{Math.round(item.confidence * 100)}%</span></div><p className="mt-3 text-sm leading-6 text-salon-text">{item.content}</p></motion.article>)}</div></motion.section>;
}

function ReviewGate({ awaitingDecision, decisionRole, canRevise, lastDecision }: { awaitingDecision?: boolean; decisionRole?: string; canRevise?: boolean; lastDecision?: string }) {
  const { t } = useTranslation();
  const style = roleStyle(decisionRole ?? "reviewer");
  return <motion.section className="salon-floating-surface px-4 py-5" variants={shellMotion} initial="hidden" animate="visible"><div className="mb-5 flex items-center gap-3"><div className="salon-role-avatar" style={{ background: `linear-gradient(135deg, rgb(${style.accent}), rgb(var(--salon-accent) / 1))` }}>{style.avatar}</div><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("reviewGate.title")}</div><h3 className="salon-display mt-1 text-2xl text-salon-text">{t("reviewGate.subtitle")}</h3></div></div><div className="grid gap-3"><FloatingTag label={t("reviewGate.awaiting")} value={String(awaitingDecision ?? false)} /><FloatingTag label={t("reviewGate.decisionRole")} value={roleLabel(decisionRole, t)} /><FloatingTag label={t("reviewGate.canRevise")} value={String(canRevise ?? false)} /><FloatingTag label={t("reviewGate.lastDecision")} value={lastDecision ?? t("app.none")} /></div></motion.section>;
}

function InterventionBar({ goal, setGoal, followup, setFollowup, selectedTaskId, onStart, onFollowup, actions, isBusy, statusHeadline, statusDetail }: { goal: string; setGoal: (value: string) => void; followup: string; setFollowup: (value: string) => void; selectedTaskId: string | null; onStart: () => Promise<void>; onFollowup: () => Promise<void>; actions: ReturnType<typeof useActions>; isBusy: boolean; statusHeadline: string; statusDetail: string }) {
  const { t } = useTranslation();
  return <motion.section className="salon-intervention-studio" variants={shellMotion} initial="hidden" animate="visible"><div className="mb-6 flex flex-wrap items-end justify-between gap-4"><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("intervention.title")}</div><h2 className="salon-display mt-2 text-3xl text-salon-text">{t("intervention.subtitle")}</h2></div><div className="text-sm text-salon-sub">{t("intervention.detail")}</div></div><div className="grid gap-4 xl:grid-cols-[minmax(0,1.2fr),minmax(0,0.95fr)]"><div className="salon-compose-panel"><div className="mb-3 text-sm font-semibold text-salon-text">{t("intervention.openSalon")}</div><textarea value={goal} onChange={(event) => setGoal(event.target.value)} className="salon-input min-h-40 resize-y p-4 text-sm" placeholder={t("intervention.frameTask")} /><div className="mt-4 flex flex-wrap gap-2"><button type="button" className={actionButtonClass(true)} onClick={() => void onStart()} disabled={!goal.trim() || actions.startMutation.isPending}>{actions.startMutation.isPending ? t("intervention.starting") : t("intervention.startSalon")}</button><button type="button" className={actionButtonClass()} onClick={() => actions.controlMutation.mutate({ action: "continue_deliberation" })} disabled={!selectedTaskId}>{t("intervention.continueDeliberation")}</button><button type="button" className={actionButtonClass()} onClick={() => actions.controlMutation.mutate({ action: "request_review" })} disabled={!selectedTaskId}>{t("intervention.requestReview")}</button><button type="button" className={actionButtonClass()} onClick={() => actions.controlMutation.mutate({ action: "enter_revise_path" })} disabled={!selectedTaskId}>{t("intervention.enterRevisePath")}</button></div></div><div className="salon-compose-panel alt"><div className="mb-3 text-sm font-semibold text-salon-text">{t("intervention.speakThread")}</div><textarea value={followup} onChange={(event) => setFollowup(event.target.value)} className="salon-input min-h-40 resize-y p-4 text-sm" placeholder={selectedTaskId ? t("intervention.followupPlaceholder") : t("intervention.selectSessionFirst")} disabled={!selectedTaskId} /><div className="mt-4 flex flex-wrap items-center gap-2"><button type="button" className={actionButtonClass(true)} disabled={!selectedTaskId || !followup.trim() || actions.followupMutation.isPending} onClick={() => void onFollowup()}>{actions.followupMutation.isPending ? t("intervention.running") : t("intervention.runNextStep")}</button><span className="salon-mini-badge">{selectedTaskId ? `${t("app.taskPrefix")} ${selectedTaskId}` : t("intervention.noTaskSelected")}</span></div></div></div>{isBusy ? <motion.div className="mt-4 salon-runtime-whisper" initial={{ opacity: 0 }} animate={{ opacity: 1 }}><div className="font-semibold text-salon-text">{statusHeadline}</div><div className="mt-1 text-sm text-salon-sub">{statusDetail}</div></motion.div> : null}</motion.section>;
}

function DevInspector({ apiBaseInput, setApiBaseInput, onApplyApiBase, roleMap, setRoleModel, paused, actions, events, language }: { apiBaseInput: string; setApiBaseInput: (value: string) => void; onApplyApiBase: () => Promise<void>; roleMap: RoleLlmMap; setRoleModel: (role: keyof RoleLlmMap, value: string) => void; paused: boolean; actions: ReturnType<typeof useActions>; events: SalonEvent[]; language: string }) {
  const { t } = useTranslation();
  return <details className="salon-floating-surface px-5 py-5"><summary className="cursor-pointer select-none text-sm font-semibold text-salon-sub">{t("inspector.title")}</summary><div className="mt-5 grid gap-4"><section className="salon-compose-panel"><div className="mb-3 text-sm font-semibold text-salon-text">{t("inspector.runtimeEndpoint")}</div><div className="flex flex-col gap-3 sm:flex-row"><input value={apiBaseInput} onChange={(event) => setApiBaseInput(event.target.value)} className="salon-input px-4 py-3 text-sm" placeholder={t("inspector.runtimeEndpointPlaceholder")} /><button type="button" className={actionButtonClass()} onClick={() => void onApplyApiBase()}>{t("inspector.apply")}</button></div></section><section className="salon-compose-panel"><div className="mb-3 text-sm font-semibold text-salon-text">{t("inspector.perRoleRouting")}</div><div className="grid gap-3 md:grid-cols-2 xl:grid-cols-4">{ROLE_TYPES.map((role) => <label key={role} className="grid gap-2"><span className="text-xs font-medium capitalize text-salon-sub">{roleLabel(role, t)}</span><input value={roleMap[role]} onChange={(event) => setRoleModel(role, event.target.value)} className="salon-input px-4 py-3 text-sm" placeholder={t("inspector.modelPlaceholder")} /></label>)}</div></section><section className="salon-compose-panel"><div className="mb-3 text-sm font-semibold text-salon-text">{t("inspector.lowLevelControls")}</div><button type="button" className={actionButtonClass()} onClick={() => actions.pauseMutation.mutate(!paused)}>{paused ? t("inspector.resumeSession") : t("inspector.pauseSession")}</button></section><section className="salon-floating-surface px-4 py-5"><div className="mb-5"><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("inspector.events")}</div><h3 className="salon-display mt-2 text-2xl text-salon-text">{t("inspector.stream")}</h3></div><div className="grid gap-3">{!events.length ? <div className="salon-whisper-panel text-sm text-salon-sub">{t("inspector.empty")}</div> : null}{events.map((event) => <article key={event.id} className="salon-note-shard"><div className="flex items-center justify-between gap-2"><div className="text-sm font-semibold text-salon-text">{translateEventType(event.type, t)}</div><div className="text-[11px] text-salon-sub">{formatTime(language, t, event.timestamp)}</div></div><div className="mt-2 text-sm text-salon-sub">{event.message}</div></article>)}</div></section></div></details>;
}

export function SalonShell() {
  const [goal, setGoal] = useState("");
  const [followup, setFollowup] = useState("");
  const [apiBaseInput, setApiBaseInput] = useState("");
  const [roleMap, setRoleMapState] = useState<RoleLlmMap>(DEFAULT_ROLE_LLM_MAP);
  const [revealedTurns, setRevealedTurns] = useState(0);
  const selectedTaskId = useUiStore((state) => state.selectedTaskId);
  const setSelectedTaskId = useUiStore((state) => state.setSelectedTaskId);
  const { t, i18n } = useTranslation();
  const runtime = useRuntime();
  const session = useSession();
  const actions = useActions();

  useEffect(() => { setApiBaseInput(getApiBase()); setRoleMapState(getRoleLlmMap()); }, []);
  useEffect(() => { const tasks = runtime.data?.tasks ?? []; if (!tasks.length) return; if (!selectedTaskId || !tasks.some((item) => item.task_id === selectedTaskId)) setSelectedTaskId(tasks[0].task_id); }, [runtime.data?.tasks, selectedTaskId, setSelectedTaskId]);

  const tasks = runtime.data?.tasks ?? [];
  const currentSession = session.data;
  const turns = currentSession?.turns ?? [];
  const paused = Boolean(runtime.data?.runtime.paused);
  const hasPendingRuntime = Boolean(runtime.data?.runtime.has_pending);
  const usingMockSource = !getApiBase();
  const isSessionRunning = Boolean(currentSession && currentSession.status !== "done" && currentSession.stage !== "done");
  const isBusy = actions.startMutation.isPending || actions.followupMutation.isPending || actions.controlMutation.isPending || actions.pauseMutation.isPending || actions.continueMutation.isPending || hasPendingRuntime || isSessionRunning;
  const focusArtifact = currentSession?.artifacts.find((artifact) => artifact.artifactId === currentSession.focusArtifactId) ?? currentSession?.artifacts.at(-1);
  const visibleTurns = turns.slice(0, revealedTurns);
  const stageDescription = currentSession?.stage ? t(`stage.stageDescriptions.${currentSession.stage}`, { defaultValue: t("stage.status.protocolWorking") }) : t("stage.status.protocolWorking");
  const statusHeadline = actions.startMutation.isPending ? t("stage.status.openingSalon") : actions.followupMutation.isPending ? t("stage.status.weavingFollowup") : actions.controlMutation.isPending ? t("stage.status.adjustingProtocol") : hasPendingRuntime ? t("stage.status.runtimeProcessing") : isSessionRunning ? turns.length ? `${roleLabel(currentSession?.activeRole, t)} ${t("stage.status.speaking")}` : t("stage.status.sessionCreated") : t("stage.status.atRest");
  const statusDetail = actions.startMutation.isPending ? t("stage.status.runtimeCreateDetail") : actions.followupMutation.isPending ? t("stage.status.followupAttached") : actions.controlMutation.isPending ? t("stage.status.controlApplied") : hasPendingRuntime ? t("stage.status.pendingLoop") : isSessionRunning ? turns.length ? `${stageDescription}${currentSession?.activeRole ? ` ${t("stage.status.activeRoleSentence")}: ${roleLabel(currentSession.activeRole, t)}.` : ""}` : t("stage.status.noRolePublished") : t("stage.status.startOrContinue");

  useEffect(() => { setRevealedTurns(0); }, [currentSession?.sessionId]);
  useEffect(() => { if (!turns.length) return void setRevealedTurns(0); if (revealedTurns > turns.length) return void setRevealedTurns(turns.length); if (revealedTurns >= turns.length) return; const timer = window.setTimeout(() => setRevealedTurns((previous) => Math.min(previous + 1, turns.length)), 420); return () => window.clearTimeout(timer); }, [revealedTurns, turns.length]);
  useEffect(() => { if (!selectedTaskId || !isBusy || paused) return; const timer = window.setInterval(() => { void session.refetch(); }, 2500); return () => window.clearInterval(timer); }, [isBusy, paused, selectedTaskId, session]);

  async function onStart() { const input = goal.trim(); if (!input) return; if (!getApiBase()) return void alert(t("intervention.mockRuntimeAlert")); setRoleLlmMap(roleMap); const response = await actions.startMutation.mutateAsync(input); setGoal(""); setSelectedTaskId(response.task_id); }
  async function onFollowup() { const taskId = selectedTaskId; const input = followup.trim(); if (!taskId || !input) return; await actions.followupMutation.mutateAsync({ taskId, input }); setFollowup(""); }
  async function onApplyApiBase() { setApiBase(apiBaseInput); await runtime.refetch(); await session.refetch(); }
  function setRoleModel(role: keyof RoleLlmMap, value: string) { const next = { ...roleMap, [role]: value }; setRoleMapState(next); setRoleLlmMap(next); }

  return <div className="salon-world min-h-screen px-4 py-6 lg:px-6"><div className="salon-ambient-orb orb-a" /><div className="salon-ambient-orb orb-b" /><div className="salon-ambient-orb orb-c" /><div className="mx-auto grid max-w-[1880px] gap-6"><SalonHeader paused={paused} usingMockSource={usingMockSource} taskCount={runtime.data?.runtime.task_count ?? 0} memoryCount={runtime.data?.runtime.memory_count ?? 0} sessionId={currentSession?.sessionId} /><main className="salon-chat-layout"><div className="salon-chat-left"><SessionNavigation selectedTaskId={selectedTaskId} setSelectedTaskId={setSelectedTaskId} tasks={tasks} /></div><motion.section className="salon-chat-stage" variants={shellMotion} initial="hidden" animate="visible"><div className="salon-chat-stage-backdrop" /><div className="salon-chat-stage-grid"><div className="salon-status-ribbon"><div><div className="text-[10px] uppercase tracking-[0.36em] text-salon-sub">{t("stage.label")}</div><h2 className="salon-display mt-3 text-3xl font-semibold text-salon-text sm:text-4xl">{statusHeadline}</h2><p className="mt-3 max-w-2xl text-sm leading-7 text-salon-sub">{statusDetail}</p></div><div className="salon-active-role"><FloatingTag label={t("stage.activeRole")} value={roleLabel(currentSession?.activeRole, t)} /></div></div><div className="salon-theatre-plate"><div className="salon-theatre-curtain curtain-left" /><div className="salon-theatre-curtain curtain-right" /><div className="salon-stage-spotlight" /><RoleEnsemble activeRole={currentSession?.activeRole} /><FocusManuscript artifact={focusArtifact} stage={currentSession?.stage} round={currentSession?.round} maxRounds={currentSession?.maxRounds} isBusy={isBusy} /></div><ProtocolPath stage={currentSession?.stage} /><ChatTimeline turns={visibleTurns} totalTurns={turns.length} activeRole={currentSession?.activeRole} language={i18n.language} /></div></motion.section><div className="salon-chat-right salon-scroll"><ArtifactLab artifacts={currentSession?.artifacts ?? []} /><MemoryPanel memory={currentSession?.memory ?? []} /><ReviewGate awaitingDecision={currentSession?.reviewGate.awaitingDecision} decisionRole={currentSession?.reviewGate.decisionRole} canRevise={currentSession?.reviewGate.canRevise} lastDecision={currentSession?.reviewGate.lastDecision} /></div></main><InterventionBar goal={goal} setGoal={setGoal} followup={followup} setFollowup={setFollowup} selectedTaskId={selectedTaskId} onStart={onStart} onFollowup={onFollowup} actions={actions} isBusy={isBusy} statusHeadline={statusHeadline} statusDetail={statusDetail} /><DevInspector apiBaseInput={apiBaseInput} setApiBaseInput={setApiBaseInput} onApplyApiBase={onApplyApiBase} roleMap={roleMap} setRoleModel={setRoleModel} paused={paused} actions={actions} events={currentSession?.events ?? []} language={i18n.language} /></div></div>;
}
