<template>
  <div class="h-100">
    <split-menu v-model="previewSplitSize" :content-props="{ class: 'h-100 pa-0' }">
      <template #menu>
        <full-height-page>
          <template #header>
            <edit-toolbar v-bind="toolbarAttrs">
              <template #title>{{ formatProjectTypeTitle(projectType) }}</template>

              <template #default>
                <s-btn-secondary
                  :loading="pdfRenderingInProgress"
                  :disabled="pdfRenderingInProgress"
                  @click="loadPdf"
                  prepend-icon="mdi-cached"
                  :text="$t('Refresh PDF')"
                >
                  <template #loader>
                    <s-saving-loader-spinner />
                    {{ $t('Refresh PDF') }}
                  </template>
                </s-btn-secondary>
              </template>
            </edit-toolbar>

            <v-tabs v-model="currentTab" grow>
              <v-tab :value="PdfDesignerTab.LAYOUT" :text="$t('Layout')" prepend-icon="mdi-flask" />
              <v-tab :value="PdfDesignerTab.HTML" text="HTML+Vue" />
              <v-tab :value="PdfDesignerTab.CSS" text="CSS" />
              <v-tab :value="PdfDesignerTab.ASSETS" :text="$t('Assets')" />
              <v-tab :value="PdfDesignerTab.PREVIEW_DATA" :text="$t('Preview Data')" />
            </v-tabs>
          </template>

          <v-window v-model="currentTab" class="h-100">
            <v-window-item :value="PdfDesignerTab.LAYOUT" class="h-100">
              <design-layout-editor
                :project-type="projectType"
                :disabled="readonly"
                @update="onUpdateCode"
                @jump-to-code="jumpToCode"
              />
            </v-window-item>
            <v-window-item :value="PdfDesignerTab.HTML" class="h-100">
              <design-code-editor
                ref="htmlEditor"
                v-model="projectType.report_template"
                language="html"
                class="h-100"
                :readonly="readonly"
              />
            </v-window-item>
            <v-window-item :value="PdfDesignerTab.CSS" class="h-100">
              <design-code-editor
                ref="cssEditor"
                v-model="projectType.report_styles"
                language="css"
                class="h-100"
                :readonly="readonly"
              />
            </v-window-item>
            <v-window-item :value="PdfDesignerTab.ASSETS" class="h-100 overflow-y-auto">
              <design-asset-manager :project-type="projectType" :disabled="readonly" />
            </v-window-item>
            <v-window-item :value="PdfDesignerTab.PREVIEW_DATA" class="h-100">
              <design-preview-data-form
                v-model="projectType.report_preview_data"
                :project-type="projectType"
                :readonly="readonly"
                v-bind="inputFieldAttrs"
              />
            </v-window-item>
          </v-window>
        </full-height-page>
      </template>

      <template #default>
        <!-- PDF preview -->
        <pdf-preview
          ref="pdfPreviewRef"
          :fetch-pdf="fetchPdf"
        />
      </template>
    </split-menu>

    <s-dialog v-model="showStartDialog">
      <template #title>{{ $t('Start Designing') }}</template>
      <template #default>
        <v-card-text>
          <p>
            {{ $t('It looks like you haven\'t started designing your report yet.') }}
            {{ $t('We recommend following approach:') }}
          </p>
          <ol class="ml-6 mt-2">
            <li>
              {{ $t('Before starting to design, define your') }}
              <nuxt-link :to="`/designs/${projectType.id}/reportfields/`" class="text-primary">{{ $t('report fields') }}</nuxt-link> {{ $t('and') }}
              <nuxt-link :to="`/designs/${projectType.id}/findingfields/`" class="text-primary">{{ $t('finding fields') }}</nuxt-link>
            </li>
            <li>{{ $t('Include base styles (click "Start Designing" below to add them)') }}</li>
            <li>{{ $t('Define the report structure in "Layout"') }}</li>
            <li>{{ $t('Customize the HTML and CSS to your needs via the code editors') }}</li>
            <li>{{ $t('Hint: Use "Preview Data" to test your design') }}</li>
          </ol>
        </v-card-text>
        <v-card-actions>
          <v-spacer />
          <s-btn-other @click="showStartDialog = false" :text="$t('Cancel')" />
          <s-btn-primary @click="startDesigning" :text="$t('Start Designing')" />
        </v-card-actions>
      </template>
    </s-dialog>
  </div>
</template>

<script setup lang="ts">
import { initialCss } from '~/components/Design/designer-components';
import { formatProjectTypeTitle, PdfDesignerTab } from "#imports";
import type { PdfPreview } from '#components';

const currentTab = ref(PdfDesignerTab.HTML);
const previewSplitSize = ref(window.innerWidth * 0.55);

const pdfPreviewRef = useTemplateRef<InstanceType<typeof PdfPreview>>('pdfPreviewRef');
const htmlEditor = useTemplateRef('htmlEditor')
const cssEditor = useTemplateRef('cssEditor')

const pdfRenderingInProgress = computed(() => pdfPreviewRef.value?.renderingInProgress);

const { projectType, toolbarAttrs, inputFieldAttrs, readonly } = useProjectTypeLockEdit(await useProjectTypeLockEditOptions({
  save: true,
  saveFields: ['report_template', 'report_styles', 'report_preview_data', 'finding_fields', 'report_sections'],
}));

async function fetchPdf(fetchOptions: { signal: AbortSignal }) {
  return await $fetch<PdfResponse>(`/api/v1/projecttypes/${projectType.value.id}/preview/`, {
    method: 'POST',
    body: projectType.value,
    ...fetchOptions,
  });
}
function loadPdf(immediate = true) {
  if (immediate) {
    pdfPreviewRef.value?.reloadImmediate();
  } else {
    pdfPreviewRef.value?.reloadDebounced();
  }
}
watch(projectType, () => loadPdf(false), { deep: true })

const showStartDialog = ref(!projectType.value.report_template && !projectType.value.report_styles && !readonly.value);
function startDesigning() {
  showStartDialog.value = false;
  projectType.value.report_styles = initialCss;
  currentTab.value = PdfDesignerTab.LAYOUT;
}

async function onUpdateCode(options: { html: string, css: string, formatHtml?: boolean, reloadPdf?: boolean }) {
  projectType.value.report_template = options.html;
  projectType.value.report_styles = options.css;
  if (options.formatHtml) {
    await nextTick();
    htmlEditor.value?.formatDocument();
  }
  if (options.reloadPdf) {
    await nextTick();
    loadPdf(true);
  }
}
async function jumpToCode(options: { tab: PdfDesignerTab, position: DocumentSelectionPosition }) {
  currentTab.value = options.tab;
  await nextTick();
  await nextTick();

  if (options.tab === PdfDesignerTab.HTML) {
    htmlEditor.value?.jumpToPosition(options.position);
  } else if (options.tab === PdfDesignerTab.CSS) {
    cssEditor.value?.jumpToPosition(options.position);
  }
}
</script>
