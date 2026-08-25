<template>
  <v-container class="pt-0">
    <h1 class="text-headline-large font-weight-bold">{{ $t('Archive Project') }}</h1>
    <p class="text-title-large mb-0">
      <strong>{{ $t('Name:') }}</strong> {{ project.name }}
    </p>

    <p>
      {{ $t('Archiving exports the project with all its data (finding, sections, notes, images, etc.) into an archive and encrypts it.') }}<br>
      {{ $t('The archive is encrypted with AES, the AES key is split using Shamir Secret Sharing into multiple parts.') }}<br>
      {{ $t('Each part is assigned to a user and encrypted with the user\'s public keys.') }}<br>
      {{ $t('The archive can only be restored if at least') }}
      <strong>{{ threshold }}</strong>
      {{ $t('users decrypt their key part with their private keys and combine them.') }}
    </p>

    <h6 class="text-title-large mt-6 mb-0">{{ $t('Users') }}</h6>
    <p>
      <strong>{{ threshold }} / {{ archiverUsers.length }}</strong> {{ $t('users are required to restore the archive.') }}<br>
      <template v-if="threshold > 1">
        {{ $t('At least {threshold} users need to work together to restore the archive.', { threshold }) }}
      </template>
    </p>

    <v-table>
      <tbody>
        <tr v-for="user in allArchiverUsers" :key="user.id">
          <td>
            {{ user.username }}<template v-if="user.name"> ({{ user.name }})</template>
          </td>
          <td>
            <v-chip v-if="user.is_global_archiver" size="small">{{ $t('Global Archiver') }}</v-chip>
            <v-chip v-else-if="user.is_project_member" size="small">{{ $t('Project Member') }}</v-chip>
          </td>
          <td>
            <p v-if="user.can_restore" class="ma-0">
              <v-icon color="green" icon="mdi-checkbox-marked" />
              {{ $t('User will be added as archiver.') }}
            </p>
            <p v-if="!user.has_permissions" class="ma-0">
              <v-icon color="warning" icon="mdi-alert" />
              {{ $t('User does not have Global Archiver permissions.') }}
            </p>
            <p v-if="!user.has_public_keys" class="ma-0">
              <v-icon color="warning" icon="mdi-alert" />
              {{ $t('User does not have any public keys. Add public keys') }}
              <strong>{{ $t('before') }}</strong>
              {{ $t('archiving the project.') }}
              <v-btn
                v-if="user.id === auth.user.value!.id"
                to="/users/self/publickeys/"
                target="_blank"
                size="small"
                color="secondary"
                prepend-icon="mdi-folder-key"
                :text="$t('Add public key')"
              />
            </p>
            <p v-if="!user.is_active" class="ma-0">
              <v-icon color="warning" icon="mdi-alert" />
              {{ $t('User is inactive.') }}
            </p>
          </td>
        </tr>
      </tbody>
    </v-table>

    <error-list :value="warnings" />
    <btn-confirm
      :disabled="!canArchive"
      :action="performArchiveProject"
      :button-text="$t('Archive Project')"
      button-icon="mdi-folder-lock-outline"
      button-color="primary-bg"
      :tooltip-text="$t('Archive Project')"
      :dialog-text="$t('Archive and encrypt this project. You need at least {threshold} of {total} users to restore this project.', { threshold, total: archiverUsers.length })"
      :confirm-input="project.name"
    />
  </v-container>
</template>

<script setup lang="ts">
import { isDeleteDateSoon } from '@base/utils/project';
import { sortBy } from "lodash-es";

const auth = useAuth();
const route = useRoute();
const apiSettings = useApiSettings();
const projectStore = useProjectStore();

const project = await useAsyncDataE(async () => await projectStore.getById(route.params.projectId as string));
const archiveCheck = await useFetchE<ArchiveCheckResult>(`/api/v1/pentestprojects/${route.params.projectId}/archive-check/`, { method: 'GET' });

const allArchiverUsers = computed(() => sortBy(archiveCheck.value.users, [u => !u.can_restore, 'created']));
const archiverUsers = computed(() => allArchiverUsers.value.filter(u => u.can_restore));
const threshold = computed(() => apiSettings.settings!.archiving_threshold!);
const canArchive = computed(() => apiSettings.settings!.features.archiving && threshold.value > 0 && threshold.value <= archiverUsers.value.length);
const warnings = computed(() => {
  const out = [] as ErrorMessage[];
  if (archiverUsers.value.length < threshold.value) {
    out.push({
      level: MessageLevel.ERROR,
      message: t('Too few archivers. At least {threshold} users are required to restore the archive.', { threshold: threshold.value }),
    });
  } else if (threshold.value === archiverUsers.value.length) {
    out.push({
      level: MessageLevel.WARNING,
      message: t('All archivers are required to restore the archive. If one user loses their key, the archive is lost forever. Consider adding more users before archiving.'),
    });
  }
  if (isDeleteDateSoon(project.value.delete_date) && apiSettings.isProfessionalLicense) {
    out.push({
      level: MessageLevel.WARNING,
      message: t('The project will be deleted in the next 7 days. Consider archiving it earlier.'),
    });
  }
  return out;
});

async function performArchiveProject() {
  const archivedProject = await $fetch<ArchivedProject>(`/api/v1/pentestprojects/${project.value.id}/archive/`, {
    method: 'POST',
    body: {}
  });
  successToast(t('Project {name} archived.', { name: archivedProject.name }));
  await navigateTo(`/projects/archived/${archivedProject.id}/`);
}
</script>
