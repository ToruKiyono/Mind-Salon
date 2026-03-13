import en from "@/locales/en/common.json";
import zh from "@/locales/zh/common.json";
import i18n from "i18next";
import { initReactI18next } from "react-i18next";

export const resources = {
  en: { common: en },
  zh: { common: zh }
} as const;

export type AppLanguage = keyof typeof resources;

export function detectBrowserLanguage(input?: string | null): AppLanguage {
  const value = (input ?? "").toLowerCase();
  if (value.startsWith("zh")) return "zh";
  return "en";
}

if (!i18n.isInitialized) {
  void i18n.use(initReactI18next).init({
    resources,
    lng: "en",
    fallbackLng: "en",
    defaultNS: "common",
    interpolation: {
      escapeValue: false
    },
    returnNull: false
  });
}

export { i18n };
