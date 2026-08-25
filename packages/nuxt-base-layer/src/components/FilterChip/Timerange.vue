<template>
  <filter-chip-base
    v-model:filter="filter"
    :filter-properties="props.filterProperties"
    :display-value="displayValue"
    @remove="emit('remove')"
  >
    <template #chip-actions>
      <s-btn-icon
        v-if="timePreset"
        icon="mdi-refresh"
        density="compact"
        size="x-small"
        class="time-refresh-btn ml-1"
        @click.stop="applyTimePreset(timePreset)"
        :title="$t('Update to current time')"
      />
    </template>
    <s-select
      v-model="timePreset"
      :label="props.filterProperties.name || filter.id"
      :items="timePresets"
      item-title="text"
      item-value="value"
      density="compact"
      class="mb-2"
      clearable
      @update:model-value="applyTimePreset"
    />

    <v-divider class="my-2"></v-divider>
    <p class="text-title-small mb-2">{{ $t('Custom Range:') }}</p>

    <s-text-field
      v-model="filter.value[0]"
      :label="$t('Start Time')"
      density="compact"
      clearable
      type="datetime-local"
      class="mb-2"
    />

    <s-text-field
      v-model="filter.value[1]"
      :label="$t('End Time')"
      density="compact"
      clearable
      type="datetime-local"
    />
  </filter-chip-base>
</template>

<script setup lang="ts">
const filter = defineModel<FilterValue>('filter', { required: true })
const props = defineProps<{
  filterProperties: FilterProperties
}>();
const emit = defineEmits(['remove']);

const displayValue = computed(() => {
  const from = filter.value.value[0]
  const to = filter.value.value[1]
  if (from && to) {
    return t('{from} until {to}', { from, to })
  } else if (from) {
    return t('From {from}', { from })
  } else if (to) {
    return t('Until {to}', { to })
  }
  return t('Any')
})

const timePreset = ref<TimeRange>('last15Min')

// Apply time preset
function applyTimePreset(timeRange: TimeRange) {
  if (!timeRange) {
    return
  }

  // For relative time presets, only set the start time, not the end time
  const now = new Date()
  const start = new Date(now)
  switch (timeRange) {
    case 'last15Min':
      start.setMinutes(start.getMinutes() - 15)
      break
    case 'lastHour':
      start.setHours(start.getHours() - 1)
      break
    case 'last3Hours':
      start.setHours(start.getHours() - 3)
      break
    case 'last12Hours':
      start.setHours(start.getHours() - 12)
      break
    case 'last24Hours':
      start.setDate(start.getDate() - 1)
      break
    case 'last7Days':
      start.setDate(start.getDate() - 7)
      break
    case 'last30Days':
      start.setDate(start.getDate() - 30)
      break
  }

  filter.value.value = [
    formatDateForInput(start),
    formatDateForInput(now),
  ]
}

// Format date for datetime-local input
function formatDateForInput(date: Date): string {
  // Format: YYYY-MM-DDThh:mm
  const year = date.getFullYear()
  const month = String(date.getMonth() + 1).padStart(2, '0')
  const day = String(date.getDate()).padStart(2, '0')
  const hours = String(date.getHours()).padStart(2, '0')
  const minutes = String(date.getMinutes()).padStart(2, '0')

  return `${year}-${month}-${day}T${hours}:${minutes}`
}

const timePresets = computed(() => [
  { text: t('Last 15 Minutes'), value: 'last15Min' },
  { text: t('Last Hour'), value: 'lastHour' },
  { text: t('Last 3 Hours'), value: 'last3Hours' },
  { text: t('Last 12 Hours'), value: 'last12Hours' },
  { text: t('Last 24 Hours'), value: 'last24Hours' },
  { text: t('Last 7 Days'), value: 'last7Days' },
  { text: t('Last 30 Days'), value: 'last30Days' }
])

// Apply default time preset on component mount
onMounted(() => {
  applyTimePreset(timePreset.value)
})

</script>
