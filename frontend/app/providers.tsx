"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import type { ReactNode } from "react";
import { useEffect, useState } from "react";
import { i18n, detectBrowserLanguage } from "@/lib/i18n";
import { LOCALES, THEMES, type LocaleId, type ThemeId, useUiStore } from "@/store/ui-store";

export function Providers({ children }: { children: ReactNode }) {
  const theme = useUiStore((s) => s.theme);
  const locale = useUiStore((s) => s.locale);
  const setTheme = useUiStore((s) => s.setTheme);
  const setLocale = useUiStore((s) => s.setLocale);
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 800
          }
        }
      })
  );

  useEffect(() => {
    const savedTheme = window.localStorage.getItem("mind-salon-theme") as ThemeId | null;
    const savedLocale = window.localStorage.getItem("mind-salon-locale") as LocaleId | null;
    const detectedLocale = detectBrowserLanguage(window.navigator.language);

    if (savedTheme && THEMES.includes(savedTheme)) {
      setTheme(savedTheme);
    }

    if (savedLocale && LOCALES.includes(savedLocale)) {
      setLocale(savedLocale);
    } else {
      setLocale(detectedLocale);
    }
  }, [setLocale, setTheme]);

  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    window.localStorage.setItem("mind-salon-theme", theme);
  }, [theme]);

  useEffect(() => {
    document.documentElement.lang = locale === "zh" ? "zh-CN" : "en";
    window.localStorage.setItem("mind-salon-locale", locale);
    void i18n.changeLanguage(locale);
  }, [locale]);

  return <QueryClientProvider client={client}>{children}</QueryClientProvider>;
}
