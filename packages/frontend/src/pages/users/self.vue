<template>
  <split-menu :content-props="{ class: 'h-100' }">
    <template #menu>
      <v-list nav density="compact">
        <v-list-item-title class="text-title-large pl-2 mb-2">{{ $t('User Profile') }}</v-list-item-title>

        <v-list-item
          to="/users/self/" exact
          prepend-icon="mdi-account"
          :title="$t('User Information')"
        />
        <v-list-item
          v-if="apiSettings.isLocalUserAuthEnabled"
          to="/users/self/security/"
          prepend-icon="mdi-lock"
          :title="$t('Security')"
        />
        <v-list-item
          to="/users/self/apitokens/"
          prepend-icon="mdi-key-variant"
          :title="$t('API Tokens')"
        />
        <v-list-item
          :disabled="!apiSettings.settings!.features.archiving"
          to="/users/self/publickeys/"
          prepend-icon="mdi-folder-key"
        >
          <v-list-item-title><pro-info>{{ $t('Archiving Public Keys') }}</pro-info></v-list-item-title>
        </v-list-item>
        <v-list-item
          to="/users/self/notifications/"
          prepend-icon="mdi-bell"
          :title="$t('Notifications')"
        />
      </v-list>
    </template>

    <template #default>
      <nuxt-page />
    </template>
  </split-menu>
</template>

<script setup lang="ts">
import { profileTitleTemplate } from "~/utils/title";

const route = useRoute();
useHead({
  titleTemplate: (title?: string|null) => profileTitleTemplate(title, route),
});
useAppBar({ breadcrumbs: [{ title: t('Profile'), to: '/users/self/' }] });
const apiSettings = useApiSettings();
</script>
