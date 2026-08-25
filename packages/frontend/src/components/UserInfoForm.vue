<template>
  <div>
    <s-card class="mt-4">
      <v-card-title>{{ $t('Login information') }}</v-card-title>
      <v-card-text>
        <v-row>
          <v-col>
            <s-text-field
              :model-value="user.username" @update:model-value="updateField('username', $event)"
              :label="$t('Username')"
              :hint="$t('Use this name for logging in')"
              autocomplete="off"
              :rules="rules.required"
              :error-messages="props.errors?.username || []"
              required
              :disabled="!canEditUsername"
              spellcheck="false"
            />
          </v-col>
          <v-col cols="auto">
            <s-color-picker
              :model-value="user.color"
              @update:model-value="updateField('color', $event)"
              :disabled="!canEdit"
            >
              <template #activator="{ props: colorPickerProps }">
                <user-avatar 
                  :user="user" 
                  size="large" 
                  class="cursor-pointer mt-1"
                  v-bind="colorPickerProps"
                />
              </template>
            </s-color-picker>
          </v-col>
        </v-row>
        <slot name="login-information" />
      </v-card-text>
    </s-card>

    <s-card class="mt-4">
      <v-card-title>{{ $t('Personal information') }}</v-card-title>
      <v-card-text>
        <v-row class="mt-4">
          <v-col :md="5">
            <s-text-field
              :model-value="user.first_name" @update:model-value="updateField('first_name', $event)"
              :label="$t('First name')"
              :rules="rules.required"
              required
              :error-messages="props.errors?.first_name || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="given-name"
            />
          </v-col>
          <v-col :md="2">
            <s-text-field
              :model-value="user.middle_name" @update:model-value="updateField('middle_name', $event)"
              :label="$t('Middle name')"
              :error-messages="props.errors?.middle_name || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="middle-name"
            />
          </v-col>
          <v-col :md="5">
            <s-text-field
              :model-value="user.last_name" @update:model-value="updateField('last_name', $event)"
              :label="$t('Last name')"
              :rules="rules.required"
              required
              :error-messages="props.errors?.last_name || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="family-name"
            />
          </v-col>
        </v-row>
        <v-row class="mt-4">
          <v-col :md="6">
            <s-text-field
              :model-value="user.title_before" @update:model-value="updateField('title_before', $event)"
              :label="$t('Title (before name)')"
              :error-messages="props.errors?.title_before || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="honorific-prefix"
            />
          </v-col>
          <v-col :md="6">
            <s-text-field
              :model-value="user.title_after" @update:model-value="updateField('title_after', $event)"
              :label="$t('Title (after name)')"
              :error-messages="props.errors?.title_after || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="honorific-suffix"
            />
          </v-col>
        </v-row>

        <s-text-field
          :model-value="user.email" @update:model-value="updateField('email', $event)"
          type="email"
          :label="$t('Email')"
          :hint="$t('Email address to receive notifications and password reset links on (if enabled)')"
          :rules="rules.required_email"
          :error-messages="props.errors?.email || []"
          :disabled="!canEditUsername"
          spellcheck="false"
          autocomplete="email"
          class="mt-8"
        />
        <v-row class="mt-4">
          <v-col :md="6">
            <s-text-field
              :model-value="user.phone" @update:model-value="updateField('phone', $event)"
              type="tel"
              :label="$t('Phone number (optional)')"
              :error-messages="props.errors?.phone || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="work tel"
            />
          </v-col>
          <v-col :md="6">
            <s-text-field
              :model-value="user.mobile" @update:model-value="updateField('mobile', $event)"
              type="tel"
              :label="$t('Mobile phone number (optional)')"
              :error-messages="props.errors?.mobile || []"
              :disabled="!canEdit"
              spellcheck="false"
              autocomplete="mobile tel"
            />
          </v-col>
        </v-row>
      </v-card-text>
    </s-card>

    <s-card class="mt-4">
      <v-card-title><pro-info>{{ $t('Permissions') }}</pro-info></v-card-title>
      <v-card-text>
        <s-checkbox
          :model-value="user.is_template_editor" @update:model-value="updateField('is_template_editor', $event)"
          :label="$t('Template Editor')"
          data-testid="template-editor-checkbox"
          :hint="$t('Template Editors are allowed to create and edit finding templates.')"
          :error-messages="props.errors?.is_template_editor || []"
          :disabled="!canEditGeneralPermissions"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_designer" @update:model-value="updateField('is_designer', $event)"
          :label="$t('Designer')"
          data-testid="designer-checkbox"
          :hint="$t('Designers can create and edit report designs. Users without this permission can create and edit private designs.')"
          :error-messages="props.errors?.is_designer || []"
          :disabled="!canEditGeneralPermissions"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_user_manager" @update:model-value="updateField('is_user_manager', $event)"
          :label="$t('User Manager')"
          data-testid="user-manager-checkbox"
          :hint="$t('User Managers can create and update other users, assign permissions and reset passwords (except superusers).')"
          :error-messages="props.errors?.is_user_manager || []"
          :disabled="!canEditGeneralPermissions"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_guest" @update:model-value="updateField('is_guest', $event)"
          :label="$t('Guest')"
          :hint="$t('Guest are not allowed to list other users and might be further restricted by your system operator.')"
          :error-messages="props.errors?.is_guest || []"
          :disabled="!canEditGeneralPermissions"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_global_archiver" @update:model-value="updateField('is_global_archiver', $event)"
          :label="$t('Global Archiver')"
          data-testid="global-archiver-checkbox"
          :hint="$t('Global Archivers will be added to archives when archiving projects (besides project members) and are able to restore these projects. They need to have archiving public keys configured for this permission take effect.')"
          :error-messages="props.errors?.is_global_archiver || []"
          :disabled="!canEditGeneralPermissions || !apiSettings.settings!.features.archiving"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_project_admin" @update:model-value="updateField('is_project_admin', $event)"
          :label="$t('Project Admin')"
          data-testid="project-admin-checkbox"
          :hint="$t('Project Admins can access and manage all projects, regardless if they are members of the project or not.')"
          :error-messages="props.errors?.is_project_admin || []"
          :disabled="!canEditGeneralPermissions"
          density="compact"
        />
        <s-checkbox
          :model-value="user.is_superuser" @update:model-value="updateField('is_superuser', $event)"
          :label="$t('Superuser')"
          :hint="$t('Superusers have the highest privileges available. They have all permissions without explicitly assigning them.')"
          :error-messages="props.errors?.is_superuser || []"
          :disabled="!canEditSuperuserPermissions"
          density="compact"
        >
          <template #label><permission-info :value="canEditSuperuserPermissions" permission-name="Superuser">{{ $t('Superuser') }}</permission-info></template>
        </s-checkbox>
        <s-checkbox
          v-if="user.is_system_user"
          :model-value="user.is_system_user"
          :label="$t('System User')"
          :hint="$t('System users have access to internal functions such as creating backups.')"
          disabled
          density="compact"
        />
      </v-card-text>
    </s-card>
  </div>
</template>

<script setup lang="ts">
const user = defineModel<User>({ required: true });
const props = defineProps<{
  errors?: any,
}>();

const auth = useAuth();
const apiSettings = useApiSettings();
const canEdit = computed(() => 
  (auth.permissions.value.user_manager && !user.value.is_superuser && !user.value.is_system_user) || 
  (auth.permissions.value.admin && !user.value.is_system_user) || 
  user.value.id === auth.user.value!.id);
const canEditUsername = computed(() => canEdit.value && auth.permissions.value.user_manager);
const canEditGeneralPermissions = computed(() => canEdit.value && auth.permissions.value.user_manager && apiSettings.settings!.features.permissions);
const canEditSuperuserPermissions = computed(() => canEdit.value && auth.permissions.value.user_manager && auth.permissions.value.admin);

const rules = {
  required: [(v: any) => !!v || t('This field is required!')],
  required_email: [(v: any) => canEditUsername.value ? rules.required[0]!(v) : true],
};

function updateField(fieldName: keyof User, val: any) {
  const newUser = Object.assign({}, user.value);
  // @ts-expect-error no readonly fields are updated
  newUser[fieldName] = val;
  user.value = newUser;
}

</script>
