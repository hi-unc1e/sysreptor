<template>
  <list-view :url="`/api/v1/pentestprojects/${project.id}/history-timeline/?mode=medium`">
    <template #title>
      {{ $t('Version History') }}
    </template>
    <template #searchbar>
      <!-- hide searchbar -->
      <span />
    </template>
    <template #items="{ items }">
      <v-timeline
        direction="vertical"
        side="end"
        align="start"
        density="compact"
        :truncate-line="items.hasNextPage.value ? 'start' : 'both'"
        class="history-timeline-content"
      >
        <history-timeline-item
          :value="{history_type: '~', history_change_reason: $t('Current Version')} as unknown as HistoryTimelineRecord"
          :to="`/projects/${project.id}/reporting/`"
        >
          <template #info><span /></template>
        </history-timeline-item>
        <history-timeline-item-project 
          v-for="item in (items.data.value as HistoryTimelineRecord[])" 
          :key="item.id" 
          :item="item" 
          :project="project" 
          :details="true"
        />
      </v-timeline>
    </template>
  </list-view>
</template>

<script setup lang="ts">
const route = useRoute();
const projectStore = useProjectStore();

const project = await useAsyncDataE(() => projectStore.getById(route.params.projectId as string));
</script>

<style lang="scss" scoped>
.history-timeline-content {
  grid-row-gap: 0;
  padding-left: 0.5em;
}
</style>
