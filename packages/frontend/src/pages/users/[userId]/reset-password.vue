<template>
  <v-form ref="formRef" @submit.prevent="changePassword">
    <v-toolbar density="compact" flat color="inherit">
      <v-toolbar-title>
        {{ $t('Reset password of {username}', { username: user.username }) }}<template v-if="user.name"> ({{ user.name }})</template>
      </v-toolbar-title>
    </v-toolbar>

    <s-password-field
      v-model="form.password"
      :label="$t('New password')"
      :error-messages="serverErrors?.password || []"
      confirm show-strength generate
      autocomplete="new-password"
      :disabled="!canEdit"
      class="mt-4"
    />

    <s-checkbox
      v-model="form.must_change_password"
      :hint="$t('The user has to change the password at the next login.')"
      :error-message="serverErrors?.must_change_password || []"
      :disabled="!canEdit || !apiSettings.isProfessionalLicense"
    >
      <template #label><pro-info>{{ $t('Must change password') }}</pro-info></template>
    </s-checkbox>

    <div class="mt-4">
      <s-btn-primary
        type="submit"
        :text="$t('Set password')"
        :disabled="!canEdit"
        class="mr-2"
      />
    </div>
  </v-form>
</template>

<script setup lang="ts">
import type { VForm } from 'vuetify/lib/components/index.mjs';

const route = useRoute();
const auth = useAuth();
const apiSettings = useApiSettings();

const user = await useFetchE<User>(`/api/v1/pentestusers/${route.params.userId}/`, { method: 'GET' });

const form = ref({
  password: '',
  must_change_password: apiSettings.isProfessionalLicense,
})
const serverErrors = ref<any|null>(null);

const canEdit = computed(() => auth.permissions.value.user_manager && !user.value!.is_system_user);

const formRef = useTemplateRef('formRef');
async function changePassword() {
  if (!((await formRef.value!.validate()).valid)) {
    return;
  }

  try {
    await $fetch(`/api/v1/pentestusers/${user.value!.id}/reset-password/`, {
      method: 'POST',
      body: form.value,
    });
    successToast(t('Password changed'));
    await navigateTo(`/users/${user.value.id}/`);
  } catch (error: any) {
    if (error?.status === 400 && error?.data) {
      serverErrors.value = error.data;
    } else {
      requestErrorToast({ error });
    }
  }
}
</script>
