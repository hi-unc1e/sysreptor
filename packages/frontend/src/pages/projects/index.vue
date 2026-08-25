<template>
  <file-drop-area @drop="importBtn?.performImport($event)" class="h-100">
    <list-view
      url="/api/v1/pentestprojects/?readonly=false"
      v-model:ordering="localSettings.projectListOrdering"
      :ordering-options="[
        {id: 'created', title: $t('Created'), value: '-created'},
        {id: 'updated', title: $t('Updated'), value: '-updated'},
        {id: 'name', title: $t('Name'), value: 'name'},
      ]"
      v-model:pinned-filters="localSettings.projectListPinnedFilters"
      :filter-properties="filterProperties"
      :selectable="true"
      ref="listViewRef"
    >
      <template #title>{{ $t('Projects') }}</template>
      <template #navigation>
        <project-navigation-dropdown value="active" />
      </template>
      <template #actions="{ selectedItems }: { selectedItems: PentestProject[] }">
        <v-divider vertical />
        <permission-info :value="auth.permissions.value.create_projects">
          <btn-create to="/projects/new/" :disabled="!auth.permissions.value.create_projects" />
        </permission-info>
        <permission-info :value="auth.permissions.value.import_projects">
          <btn-import ref="importBtn" :import="performImport" :disabled="!auth.permissions.value.import_projects" />
        </permission-info>
        <template v-if="selectedItems.length > 0">
          <v-divider vertical />
          <s-btn-icon
            color="secondary"
            variant="flat"
            density="comfortable"
            v-tooltip.bottom="$t('Export selected')"
          >
            <v-icon icon="mdi-download" />
            <v-menu activator="parent" location="bottom">
              <v-list>
                <btn-export
                  export-url="/api/v1/pentestprojects/export/"
                  :options="{ids: selectedItems.map(p => p.id), export_all: false}"
                  name="projects"
                  extension=".tar.gz"
                />
                <btn-export
                  export-url="/api/v1/pentestprojects/export/"
                  :options="{ids: selectedItems.map(p => p.id), export_all: true}"
                  name="projects"
                  extension=".tar.gz"
                  :button-text="$t('Export (with notes)')"
                />
              </v-list>
            </v-menu>
          </s-btn-icon>
          <permission-info :value="auth.permissions.value.update_project_settings">
            <btn-readonly
              :value="false"
              :set-readonly="() => setReadonlySelected(selectedItems)"
              :disabled="!auth.permissions.value.update_project_settings"
              :show-toast="false"
              button-variant="icon"
              variant="flat"
              density="comfortable"
            >
              <template #dialog-text>
                <p class="mt-0">
                  {{ $t('Mark {count} projects as finished and make them readonly?', { count: selectedItems.length }) }}
                </p>
                <ul class="mt-0">
                  <li v-for="p in selectedItems" :key="p.id">
                    {{ p.name }}
                  </li>  
                </ul>
              </template>
            </btn-readonly>
          </permission-info>
          <permission-info :value="auth.permissions.value.delete_projects">
            <btn-delete
              :delete="() => performDeleteSelected(selectedItems)"
              :disabled="!auth.permissions.value.delete_projects"
              :confirm-input="$t('delete {count} projects', { count: selectedItems.length })"
              :tooltip-text="$t('Delete selected')"
              icon="mdi-delete"
              density="comfortable"
            >
              <template #dialog-text>
                <p class="mt-0">
                  {{ $t('Do you really want to delete {count} projects?', { count: selectedItems.length }) }}
                </p>
                <ul class="mt-0">
                  <li v-for="p in selectedItems" :key="p.id">
                    {{ p.name }}
                  </li>
                </ul>
              </template>
            </btn-delete>
          </permission-info>
        </template>
      </template>
      <template #item="{item}: {item: PentestProject}">
        <project-list-item :item="item" @filter="listViewRef?.addFilter($event)" />
      </template>
    </list-view>
  </file-drop-area>
</template>

<script setup lang="ts">
import { useProjectTags } from '@base/composables/tags';
import { sortBy, uniq } from 'lodash-es';

definePageMeta({
  title: 'Projects',
  toplevel: true,
});
useAppBar({ breadcrumbs: projectListBreadcrumbs() });

const auth = useAuth();
const localSettings = useLocalSettings();
const apiSettings = useApiSettings();
const projectStore = useProjectStore();

const importBtn = useTemplateRef('importBtn');
async function performImport(file: File) {
  const projects = await uploadFileHelper<PentestProject[]>('/api/v1/pentestprojects/import/', file);
  await navigateTo(`/projects/${projects[0]!.id}/`);
}

const listViewRef = useTemplateRef('listViewRef');
const suggestedMembers = ref<string[]>([]);
watch(() => listViewRef.value?.items?.data.value as PentestProject[]|undefined, (items) => {
  if (!items) { return; }
  suggestedMembers.value = sortBy(uniq(items.flatMap(p => p.members.map(member => member.username)).concat(suggestedMembers.value)));
}, { immediate: true, deep: 1 });
const suggestedTags = useProjectTags();
const filterProperties = computed((): FilterProperties[] => [
  { id: 'member', name: t('Member'), icon: 'mdi-account', type: 'combobox', options: suggestedMembers.value, allow_exclude: true, allow_regex: false, default: '', multiple: true },
  { id: 'tag', name: t('Tag'), icon: 'mdi-tag', type: 'combobox', options: suggestedTags.getTags, allow_exclude: true, allow_regex: false, default: '', multiple: true },
  { id: 'timerange', name: t('Time Created'), icon: 'mdi-calendar', type: 'daterange', options: [], allow_exclude: true, default: '', multiple: true },
  { id: 'language', name: t('Language'), icon: 'mdi-translate', type: 'select', options: apiSettings.settings!.languages.map(l => l.code), allow_exclude: true, default: '', multiple: true },
  { id: 'name', name: t('Name'), type: 'text', options: [], allow_exclude: true, allow_regex: false, default: '', multiple: true },
]);

async function performDeleteSelected(projects: PentestProject[]) {
  await bulkAction(projects, projectStore.deleteProject, p => t('Failed to delete "{name}"', { name: p.name }));
  await listViewRef.value?.refresh();
}
async function setReadonlySelected(projects: PentestProject[]) {
  await bulkAction(projects, p => projectStore.setReadonly(p, true), p => t('Failed to finish "{name}"', { name: p.name }));
  await listViewRef.value?.refresh();
}

</script>
