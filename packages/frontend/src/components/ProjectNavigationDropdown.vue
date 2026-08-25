<template>
  <navigation-dropdown
    :value="props.value"
    :items="[
      {
        value: 'active',
        title: $t('Active Projects'),
        icon: 'mdi-file-document',
        to: { path: '/projects/', query: route.query }
      },
      {
        value: 'finished',
        title: $t('Finished'),
        icon: 'mdi-flag-checkered',
        to: { path: '/projects/finished/', query: route.query }
      },
      {
        value: 'archived',
        title: $t('Archived'),
        icon: 'mdi-folder-lock-outline',
        disabled: !apiSettings.settings!.features.archiving,
        to: { path: '/projects/archived/', query: route.query }
      },
    ]"
  />
</template>

<script setup lang="ts">
const props = defineProps<{
  value: string;
}>();

const apiSettings = useApiSettings();
const route = useRoute();
</script>
