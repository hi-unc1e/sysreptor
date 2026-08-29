<template>
  <v-container class="h-100 overflow-y-auto">
    <h1 class="text-headline-large font-weight-bold mb-0">{{ $t('Backup') }}</h1>
    <p class="text-body-medium text-medium-emphasis mt-2 mb-6">
      {{ $t('Download or restore your report designs, finding templates and projects without a Professional license or BACKUP_KEY.') }}
    </p>

    <s-card :title="$t('Community Data Backup')">
      <template #text>
        <p>
          {{ $t('Export all report designs, finding templates and projects as a single .tar.gz file, or restore them from such a file. Imports always create new copies and never overwrite existing data.') }}
        </p>
        <div class="d-flex align-center ga-4 flex-wrap">
          <btn-confirm
            :action="exportAllData"
            :confirm="false"
            :button-text="$t('Export All Data')"
            button-icon="mdi-download"
            button-color="primary-bg"
          />
          <v-file-input
            v-model="importFile"
            accept=".tar.gz,.tgz,.gz,.tar"
            :label="$t('Import backup file')"
            hide-details
            density="compact"
            class="import-file-input"
          />
          <btn-confirm
            :action="importAllData"
            :confirm="false"
            :button-text="$t('Import Data')"
            button-icon="mdi-upload"
            button-color="primary-bg"
            :disabled="!importFile"
          />
        </div>
      </template>
    </s-card>

    <s-card :title="$t('Backup History')" class="mt-8">
      <template #text>
        <v-table>
          <thead>
            <tr>
              <th>{{ $t('Date') }}</th>
              <th>{{ $t('User') }}</th>
              <th>{{ $t('Description') }}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="log in backupLogs.data.value" :key="log.id">
              <td><chip-date :value="log.created" /></td>
              <td>{{ log.user || '-' }}</td>
              <td>
                <template v-if="log.type === BackupLogType.SETUP">{{ $t('Set up SysReptor instance') }}</template>
                <template v-else-if="log.type === BackupLogType.BACKUP_STARTED">{{ $t('Backup started') }}</template>
                <template v-else-if="log.type === BackupLogType.BACKUP_FINISHED">{{ $t('Backup finished') }}</template>
                <template v-else-if="log.type === BackupLogType.RESTORE">{{ $t('Restored backup') }}</template>
                <template v-else>{{ log.type }}</template>
              </td>
            </tr>
          </tbody>
        </v-table>
        <page-loader :items="backupLogs" />
      </template>
    </s-card>

    <v-expansion-panels class="mt-8" variant="accordion">
      <v-expansion-panel>
        <v-expansion-panel-title>
          {{ $t('Advanced: full instance backup (requires BACKUP_KEY)') }}
        </v-expansion-panel-title>
        <v-expansion-panel-text>
          <p v-if="!apiSettings.settings!.features.backup">
            {{ $t('No backup key configured.') }} <br><br>
            {{ $t('You need to configure a') }} <v-code tag="span">BACKUP_KEY</v-code> {{ $t('as environment variable. This backup key has to be at least 20 characters long. If no') }} <v-code tag="span">BACKUP_KEY</v-code> {{ $t('is configured, the backup API endpoint is disabled.') }}
          </p>
          <p v-else>
            {{ $t('Enter the configured') }} <v-code tag="span">BACKUP_KEY</v-code> {{ $t('to create a backup of this SysReptor instance (see') }}
            <a href="https://docs.sysreptor.com/setup/configuration/#backup-key" target="_blank" class="text-primary">https://docs.sysreptor.com/setup/configuration/#backup-key</a>{{ $t(').') }}
          </p>

          <s-password-field
            v-model="backupKey"
            :label="$t('Backup Key')"
            :rules="rules.backupKey"
            :error-messages="backupKeyError"
            :hide-details="false"
            :disabled="!apiSettings.settings!.features.backup"
            class="mt-4"
          />
          <btn-confirm
            :action="createBackup"
            :confirm="false"
            :button-text="$t('Download Backup')"
            button-icon="mdi-download"
            button-color="primary-bg"
            :disabled="!apiSettings.settings!.features.backup"
            class="mt-2"
          />
          <form
            v-if="renderDownloadForm"
            ref="downloadForm"
            action="/api/v1/utils/backup/"
            method="POST"
            target="_blank"
          >
            <input type="hidden" name="key" :value="backupKey" />
            <input type="hidden" name="csrfmiddlewaretoken" :value="csrftoken" />
          </form>
        </v-expansion-panel-text>
      </v-expansion-panel>
    </v-expansion-panels>
  </v-container>
</template>

<script setup lang="ts">
import { BackupLogType } from '#imports';

definePageMeta({
  title: 'Backup',
  toplevel: true,
});
useAppBar({ breadcrumbs: [{ title: 'Backup', to: '/backups/' }] });

const auth = useAuth();
const csrftoken = useCookie('csrftoken');
const apiSettings = useApiSettings();

await useAsyncDataE(async () => {
  if (!auth.permissions.value.view_backup) {
    await navigateTo('/');
  }
});

const backupLogs = useSearchableCursorPaginationFetcher<BackupLog>({
  baseURL: '/api/v1/utils/backuplogs/',
});

const backupKey = ref('');
const backupKeyError = ref<string|null>(null);
const rules = {
  backupKey: [
    (v: string) => !!v || t('Backup Key is required'),
    (v: string) => v.length >= 20 || t('Backup Key must be at least 20 characters long'),
  ],
}

const renderDownloadForm = ref(false);
const downloadForm = useTemplateRef('downloadForm');
async function createBackup() {
  try {
    // Check permissions and backup key
    // for error handling in frontend
    backupKeyError.value = null;
    await $fetch.raw('/api/v1/utils/backup/', {
      method: 'POST',
      body: {
        key: backupKey.value,
        check: true,
      },
    });

    // Download backup via native browser mechanisms
    renderDownloadForm.value = true;
    await nextTick();
    downloadForm.value?.submit();
    await nextTick()
    renderDownloadForm.value = false;
  } catch (error: any) {
    backupKeyError.value = error.data?.detail || error.data?.key;
    if (!backupKeyError.value) {
      throw error;
    }
  }
}

const importFile = ref<File|null>(null);
async function exportAllData() {
  const response = await $fetch.raw('/api/v1/utils/export_all/', {
    method: 'POST',
  });
  const blob = response._data as Blob;
  const url = URL.createObjectURL(blob);
  const link = document.createElement('a');
  link.href = url;
  link.download = `sysreptor-backup-${new Date().toISOString().slice(0, 19).replace(/[T:]/g, '-')}.tar.gz`;
  link.click();
  URL.revokeObjectURL(url);
}

async function importAllData() {
  const file = importFile.value;
  if (!file) {
    return;
  }
  const formData = new FormData();
  formData.append('file', file);
  const result = await $fetch<{ designs: number, templates: number, projects: number }>('/api/v1/utils/import_all/', {
    method: 'POST',
    body: formData,
  });
  successToast(t('Imported {designs} designs, {templates} templates, {projects} projects', result));
  importFile.value = null;
}
</script>

<style scoped>
.import-file-input {
  max-width: 320px;
}
</style>
