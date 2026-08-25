<template>
  <v-select
    :items="UI_LOCALES"
    :model-value="localeStore.locale"
    :label="hideLabel ? undefined : $t('Language')"
    prepend-inner-icon="mdi-translate"
    hide-details
    density="compact"
    variant="underlined"
    @update:model-value="localeStore.setLocale($event as UiLocale)"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  hideLabel?: boolean;
}>();
void props;

const localeStore = useLocaleStore();
</script>
