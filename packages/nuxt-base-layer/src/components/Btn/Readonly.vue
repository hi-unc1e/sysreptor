<template>
  <btn-confirm
    v-if="props.value"
    :action="() => performAction(false)"
    :confirm="true"
    :button-text="$t('Re-activate')"
    button-icon="mdi-reload"
    :tooltip-text="$t('Mark as active and allow editing')"
    :dialog-text="$t('Mark this project as active and allow editing.')"
  >
    <template v-for="(_, name) in $slots" #[name]="slotData: any"><slot :name="name" v-bind="slotData" /></template>
  </btn-confirm>
  <btn-confirm
    v-else
    :action="() => performAction(true)"
    :confirm="true"
    :button-text="$t('Finish')"
    button-icon="mdi-flag-checkered"
    :tooltip-text="$t('Mark as finished and make readonly')"
  >
    <template #dialog-text>
      <slot name="dialog-text">
        <p class="mt-0">
          {{ $t('Mark this project as finished and make it readonly. You and other users will not be able to edit this project, sections and findings.') }}
        </p>
        <v-alert v-if="isDeleteDateSoon(project?.delete_date) && apiSettings.isProfessionalLicense" type="warning">
          {{ $t('The project is configured to be automatically deleted at {date}', { date: project?.delete_date }) }}
        </v-alert>
      </slot>
    </template>
    <template v-for="(_, name) in $slots" #[name]="slotData: any"><slot :name="name" v-bind="slotData" /></template>
  </btn-confirm>
</template>

<script setup lang="ts">
import { isDeleteDateSoon } from '@base/utils/project';

const props = defineProps<{
  value: boolean;
  setReadonly: (val: boolean) => Promise<void>;
  showToast?: boolean;
  project?: PentestProject;
}>();

const apiSettings = useApiSettings();

async function performAction(val: boolean) {
  await props.setReadonly(val);
  if (props.showToast) {
    if (val) {
      successToast(t('Finished project'));
    } else {
      successToast(t('Re-activated project'));
    }
  }
}
</script>
