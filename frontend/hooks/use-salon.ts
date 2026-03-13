"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { continueSalon, controlSession, fetchRuntimeState, fetchSession, followupSalon, pauseSalon, startSalon } from "@/lib/api";
import { useUiStore } from "@/store/ui-store";

export function useRuntime() {
  return useQuery({
    queryKey: ["runtime"],
    queryFn: fetchRuntimeState
  });
}

export function useSession() {
  const taskId = useUiStore((s) => s.selectedTaskId);
  return useQuery({
    queryKey: ["session", taskId],
    queryFn: () => fetchSession(taskId as string),
    enabled: Boolean(taskId)
  });
}

export function useActions() {
  const query = useQueryClient();
  const taskId = useUiStore((s) => s.selectedTaskId);
  const invalidate = async () => {
    await query.invalidateQueries({ queryKey: ["runtime"] });
    await query.invalidateQueries({ queryKey: ["session"] });
  };

  return {
    startMutation: useMutation({ mutationFn: startSalon, onSuccess: invalidate }),
    followupMutation: useMutation({
      mutationFn: ({ taskId, input }: { taskId: string; input: string }) => followupSalon(taskId, input),
      onSuccess: invalidate
    }),
    controlMutation: useMutation({
      mutationFn: ({ action, payload }: { action: "continue_deliberation" | "request_review" | "enter_revise_path" | "pause_session" | "human_intervention" | "replay_round"; payload?: Record<string, unknown> }) => {
        if (!taskId) throw new Error("No selected task.");
        return controlSession(taskId, action, payload);
      },
      onSuccess: invalidate
    }),
    pauseMutation: useMutation({ mutationFn: pauseSalon, onSuccess: invalidate }),
    continueMutation: useMutation({ mutationFn: continueSalon, onSuccess: invalidate })
  };
}
