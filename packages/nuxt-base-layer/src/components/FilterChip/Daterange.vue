<template>
  <filter-chip-base
    v-model:filter="filter"
    :filter-properties="props.filterProperties"
    :display-value="displayValue"
    @remove="emit('remove')"
  >
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
      type="date"
      density="compact"
      clearable
      class="mb-2"
    />

    <s-text-field
      v-model="filter.value[1]"
      :label="$t('End Time')"
      type="date"
      density="compact"
      clearable
    />
  </filter-chip-base>
</template>

<script setup lang="ts">
const filter = defineModel<FilterValue>('filter', { required: true });
const props = defineProps<{
  filterProperties: FilterProperties;
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
const timePreset = ref<DateRange>('last12Months')

// Apply time preset
function applyTimePreset(timeRange: DateRange) {
  if (!timeRange) {
    return
  }

  // For relative time presets, only set the start time, not the end time
  const now = new Date()
  const start = new Date(now)
  switch (timeRange) {
    case 'last24Hours':
      start.setDate(start.getDate() - 1)
      break
    case 'last7Days':
      start.setDate(start.getDate() - 7)
      break
    case 'last30Days':
      start.setDate(start.getDate() - 30)
      break
    case 'last90Days':
      start.setDate(start.getDate() - 90)
      break
    case 'last12Months':
      start.setMonth(start.getMonth() - 12)
      break
    case 'last24Months':
      start.setMonth(start.getMonth() - 24)
      break
    case 'last5Years':
      start.setFullYear(start.getFullYear() - 5)
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

  return `${year}-${month}-${day}`
}

const timePresets = computed(() => [
  { text: t('Last 24 Hours'), value: 'last24Hours' },
  { text: t('Last 7 Days'), value: 'last7Days' },
  { text: t('Last 30 Days'), value: 'last30Days' },
  { text: t('Last 90 Days'), value: 'last90Days' },
  { text: t('Last 12 Months'), value: 'last12Months' },
  { text: t('Last 24 Months'), value: 'last24Months' },
  { text: t('Last 5 Years'), value: 'last5Years' }
])

// Apply default time preset on component mount
onMounted(() => {
  applyTimePreset(timePreset.value)
})

</script>
