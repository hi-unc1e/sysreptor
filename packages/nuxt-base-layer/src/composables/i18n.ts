import { defineStore } from 'pinia';
import { zhCN as dateFnsZhCN, enUS as dateFnsEnUS } from 'date-fns/locale';

export type UiLocale = 'en' | 'zh-CN';

export const UI_LOCALES: ReadonlyArray<{ value: UiLocale; title: string }> = [
  { value: 'en', title: 'English' },
  { value: 'zh-CN', title: '简体中文' },
];

// Merge all dictionary fragments (one JSON file per UI area) into a single lookup table.
// Keys are the English source strings; missing translations fall back to the key itself.
const zhCNDictionaryModules = import.meta.glob('../locales/zh-CN/*.json', { eager: true, import: 'default' }) as Record<string, Record<string, string>>;
const zhCNMessages: Record<string, string> = Object.assign({}, ...Object.values(zhCNDictionaryModules));

function detectLocale(): UiLocale {
  try {
    if (typeof navigator !== 'undefined' && navigator.language?.toLowerCase().startsWith('zh')) {
      return 'zh-CN';
    }
  } catch { /* ignore */ }
  return 'en';
}

export const useLocaleStore = defineStore('ui-locale', {
  state: () => ({
    locale: detectLocale(),
  }),
  actions: {
    setLocale(locale: UiLocale) {
      this.locale = locale;
    },
  },
  persist: {
    storage: localStorage,
  },
});

function getLocale(): UiLocale {
  try {
    return useLocaleStore().locale;
  } catch {
    // No active pinia (e.g. outside app context)
    return 'en';
  }
}

export function useI18n() {
  const store = useLocaleStore();
  return {
    locale: computed<UiLocale>(() => store.locale),
    setLocale: (locale: UiLocale) => store.setLocale(locale),
    t,
  };
}

export function t(key: string, params?: Record<string, string | number>): string {
  const locale = getLocale();
  let text = locale === 'zh-CN' ? (zhCNMessages[key] ?? key) : key;
  if (params) {
    for (const [name, value] of Object.entries(params)) {
      text = text.split(`{${name}}`).join(String(value));
    }
  }
  return text;
}

export function getDateFnsLocale() {
  return getLocale() === 'zh-CN' ? dateFnsZhCN : dateFnsEnUS;
}
