"use client";

import { useTranslation } from "react-i18next";
import { THEMES, type ThemeId, useUiStore } from "@/store/ui-store";

export function ThemeSwitcher() {
  const theme = useUiStore((s) => s.theme);
  const setTheme = useUiStore((s) => s.setTheme);
  const { t } = useTranslation();

  return (
    <div className="grid gap-3">
      {THEMES.map((item) => {
        const active = item === theme;
        const chips = t(`theme.${item}.chips`, { returnObjects: true }) as string[];

        return (
          <button
            key={item}
            type="button"
            onClick={() => setTheme(item as ThemeId)}
            className={`salon-theme-card ${active ? "is-active" : ""}`}
          >
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-sm font-semibold text-salon-text">{t(`theme.${item}.label`)}</div>
                <div className="mt-1 text-xs leading-5 text-salon-sub">{t(`theme.${item}.note`)}</div>
              </div>
              {active ? <span className="salon-mini-badge">{t("app.live")}</span> : null}
            </div>
            <div className="salon-theme-swatches">
              <span />
              <span />
              <span />
            </div>
            <div className="flex flex-wrap gap-2">
              {chips.map((chip) => (
                <span key={chip} className="salon-mini-badge">{chip}</span>
              ))}
            </div>
          </button>
        );
      })}
    </div>
  );
}
