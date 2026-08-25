<template>
  <full-height-page>
    <s-sub-drawer>
      <template #default="{ isExpanded }">
        <v-list-item :to="`/designs/${route.params.projectTypeId}/`" exact prepend-icon="mdi-cogs" :title="$t('Settings')">
          <v-tooltip v-if="!isExpanded" activator="parent" :text="$t('Settings')" />
        </v-list-item>
        <v-list-item :to="`/designs/${route.params.projectTypeId}/pdfdesigner/`" prepend-icon="mdi-pencil-ruler" :title="$t('PDF Designer')">
          <v-tooltip v-if="!isExpanded" activator="parent" :text="$t('PDF Designer')" />
        </v-list-item>
        <v-list-item :to="`/designs/${route.params.projectTypeId}/reportfields/`" prepend-icon="mdi-alpha-r-box" :title="$t('Report Fields')">
          <v-tooltip v-if="!isExpanded" activator="parent" :text="$t('Report Fields')" />
        </v-list-item>
        <v-list-item :to="`/designs/${route.params.projectTypeId}/findingfields/`" prepend-icon="mdi-alpha-f-box" :title="$t('Finding Fields')">
          <v-tooltip v-if="!isExpanded" activator="parent" :text="$t('Finding Fields')" />
        </v-list-item>
        <v-list-item :to="`/designs/${route.params.projectTypeId}/notes/`" prepend-icon="mdi-notebook" :title="$t('Notes')">
          <v-tooltip v-if="!isExpanded" activator="parent" :text="$t('Notes')" />
        </v-list-item>
      </template>
    </s-sub-drawer>

    <nuxt-page />
  </full-height-page>
</template>

<script setup lang="ts">
const route = useRoute();
const projectTypeStore = useProjectTypeStore();

await useAsyncDataE(async () => await projectTypeStore.getById(route.params.projectTypeId as string));
const projectType = computed(() => projectTypeStore.projectType(route.params.projectTypeId as string));

useHead({
  titleTemplate: title => designTitleTemplate(projectType.value, title, route),
});
useAppBar({ breadcrumbs: () => designDetailBreadcrumbs(projectType.value) });
</script>
