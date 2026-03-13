"use client";

import { i18n } from "@/lib/i18n";
import { useTranslation } from "react-i18next";
import { type LocaleId, useUiStore } from "@/store/ui-store";

const LANGUAGES: LocaleId[] = ["en", "zh"];

export function LanguageSwitcher() {
  const locale = useUiStore((state) => state.locale);
  const setLocale = useUiStore((state) => state.setLocale);
  const { t } = useTranslation();

  function onChange(next: LocaleId) {
    setLocale(next);
    void i18n.changeLanguage(next);
  }

  return (
    <div className="salon-language-switcher">
      <span className="text-[10px] uppercase tracking-[0.28em] text-salon-sub">{t("app.language")}</span>
      <div className="mt-2 flex gap-2">
        {LANGUAGES.map((item) => (
          <button
            key={item}
            type="button"
            className={`salon-lang-pill ${locale === item ? "is-active" : ""}`}
            onClick={() => onChange(item)}
          >
            {item === "en" ? t("app.english") : t("app.chinese")}
          </button>
        ))}
      </div>
    </div>
  );
}
