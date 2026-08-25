import { t } from '../composables/i18n';

declare module 'vue' {
  interface GlobalProperties {
    $t: typeof t;
  }
}

declare module '#app' {
  interface NuxtApp {
    $t: typeof t;
  }
}

export default defineNuxtPlugin((nuxtApp) => {
  nuxtApp.vueApp.config.globalProperties.$t = t;
  nuxtApp.provide('t', t);
});
