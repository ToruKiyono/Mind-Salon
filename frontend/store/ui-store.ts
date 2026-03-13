import { create } from "zustand";

export const THEMES = ["youthful-girl", "wuxia-princess", "tech-sci-fi"] as const;
export const LOCALES = ["en", "zh"] as const;

export type ThemeId = (typeof THEMES)[number];
export type LocaleId = (typeof LOCALES)[number];

type UiState = {
  selectedTaskId: string | null;
  theme: ThemeId;
  locale: LocaleId;
  setSelectedTaskId: (id: string | null) => void;
  setTheme: (theme: ThemeId) => void;
  setLocale: (locale: LocaleId) => void;
};

export const useUiStore = create<UiState>((set) => ({
  selectedTaskId: null,
  theme: "youthful-girl",
  locale: "en",
  setSelectedTaskId: (id) => set({ selectedTaskId: id }),
  setTheme: (theme) => set({ theme }),
  setLocale: (locale) => set({ locale })
}));
