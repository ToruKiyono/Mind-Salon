# i18n System

## Overview

Mind Salon now uses `react-i18next` with `i18next` as the canonical translation layer for the frontend theatre interface.

The system is designed so that all visible UI copy flows through translation keys instead of component-level hardcoded strings.

## Files

- `frontend/lib/i18n.ts`
  Initializes `i18next`, registers locale resources, and provides browser-language detection.
- `frontend/locales/en/common.json`
  English source strings.
- `frontend/locales/zh/common.json`
  Chinese source strings.
- `frontend/components/language-switcher.tsx`
  Header language switcher using `i18n.changeLanguage("en")` and `i18n.changeLanguage("zh")`.
- `frontend/app/providers.tsx`
  Syncs Zustand UI state, browser detection, local storage persistence, and document language.

## Language Flow

1. On startup, the provider reads `mind-salon-locale` from local storage.
2. If no saved language exists, the provider detects `navigator.language`.
3. The detector maps browser locales beginning with `zh` to `zh`; all others fall back to `en`.
4. The provider updates `i18next` via `i18n.changeLanguage(...)`.
5. UI components read translated strings with `useTranslation()`.

Fallback language is English.

## Authoring Rules

- All user-facing UI copy must live in `common.json` locale files.
- Components should render copy with `t("...")`.
- Role labels, protocol stages, status copy, theme labels, and inspector text all belong in translations.
- Dynamic runtime values such as artifact ids, timestamps, versions, and backend payload text may still be rendered directly.

## Extending Languages

To add a new language later:

1. Create a new locale file such as `frontend/locales/ja/common.json`.
2. Register it in `frontend/lib/i18n.ts`.
3. Add the locale id to `frontend/store/ui-store.ts`.
4. Extend `frontend/components/language-switcher.tsx` with a new option.

## Theatre UI Coverage

The translation system currently covers:

- header and session status
- language switcher
- theme switcher
- session atlas
- salon stage and protocol path
- focus manuscript
- role chat timeline and thought blocks
- artifact lab, memory, and review gate
- intervention command bar
- developer inspector

This keeps the AI Theatre Interface bilingual while remaining scalable for additional locales.
