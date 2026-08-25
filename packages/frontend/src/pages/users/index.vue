<template>
  <list-view
    url="/api/v1/pentestusers/"
    v-model:ordering="localSettings.userListOrdering"
    :ordering-options="[
      {id: 'created', title: $t('Created'), value: '-created'},
      {id: 'updated', title: $t('Updated'), value: '-updated'},
      {id: 'name', title: $t('Name'), value: 'username'},
    ]"
  >
    <template #title>{{ $t('Users') }}</template>
    <template #actions>
      <btn-create 
        to="/users/new/" 
        :disabled="!auth.permissions.value.user_manager"
      />
    </template>
    <template #item="{item: user}: {item: User}">
      <v-list-item :to="`/users/${user.id}/`">
        <v-row>
          <v-col md="3">
            <v-list-item-title :data-testid="`user-${user.username}`">
              <user-avatar :user="user" class="mr-2" />
              {{ user.username }}
              <template v-if="user.name">
                ({{ user.name }})
              </template>
            </v-list-item-title>
          </v-col>
          <v-col md="3">
            <v-chip size="small" class="ma-1" v-if="user.is_superuser" :text="$t('Superuser')" />
            <v-chip size="small" class="ma-1" v-if="user.is_project_admin" :text="$t('Project Admin')" />
            <v-chip size="small" class="ma-1" v-if="user.is_user_manager" :text="$t('User Manager')" />
            <v-chip size="small" class="ma-1" v-if="user.is_designer" :text="$t('Designer')" />
            <v-chip size="small" class="ma-1" v-if="user.is_template_editor" :text="$t('Template Editor')" />
            <v-chip size="small" class="ma-1" v-if="user.is_guest" :text="$t('Guest')" />
            <v-chip size="small" class="ma-1" v-if="user.is_global_archiver" :text="$t('Global Archiver')" />
            <v-chip size="small" class="ma-1" v-if="user.is_system_user" :text="$t('System')" />
          </v-col>
          <v-col md="1">
            <v-chip size="small" class="ma-1" v-if="!user.is_system_user">
              <v-icon v-if="user.is_mfa_enabled" color="green" icon="mdi-check" />
              <v-icon v-else color="red" icon="mdi-close" />
              MFA
            </v-chip>
          </v-col>
          <v-col md="2">
            <v-chip size="small" class="ma-1" v-if="!user.is_system_user">{{ $t('Last Login: {date}', { date: (user.last_login || $t('never')).split('T')[0] }) }}</v-chip>
          </v-col>
          <v-col md="1">
            <v-chip size="small" class="ma-1" color="warning" v-if="!user.is_active">{{ $t('Inactive') }}</v-chip>
          </v-col>
        </v-row>
      </v-list-item>
    </template>
  </list-view>
</template>

<script setup lang="ts">
definePageMeta({
  title: 'Users',
  toplevel: true,
});
useAppBar({ breadcrumbs: userListBreadcrumbs() });

const auth = useAuth();
const localSettings = useLocalSettings();
</script>
