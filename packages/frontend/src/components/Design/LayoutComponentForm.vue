<template>
  <div>
    <div v-if="['headline', 'section-create'].includes(form.form)">
      <s-text-field
        v-model="form.headline.text"
        :label="$t('Headline')"
        :disabled="props.disabled"
        spellcheck="false"
        class="mb-4"
      />
      <s-select
        v-model.number="form.headline.tag"
        :items="['h1', 'h2', 'h3', 'h4', 'h5', 'h6']"
        :label="$t('Tag')"
        :disabled="props.disabled"
      />
      <s-checkbox
        v-model="form.headline.intoc"
        :label="$t('Include in Table of Contents')"
        :disabled="props.disabled"
      />
      <s-checkbox
        v-model="form.headline.numbered"
        :label="$t('Prepend chapter number')"
        :disabled="props.disabled"
        class="mb-4"
      />
    </div>
    <div v-if="['markdown-create', 'section-create'].includes(form.form)">
      <s-select
        v-model="form.markdown.form"
        :items="['text', 'variable']"
        :label="$t('Markdown Type')"
        :disabled="props.disabled"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'markdown-text' || (['markdown-create', 'section-create'].includes(form.form) && form.markdown.form === 'text')">
      <markdown-field
        v-model="form.markdown.text"
        :label="$t('Markdown')"
        v-bind="markdownProps"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'markdown-variable' || (['markdown-create', 'section-create'].includes(form.form) && form.markdown.form === 'variable')">
      <!-- TODO: autocomplete report/finding variables (ComboBox - allow other values) -->
      <s-text-field
        v-model="form.markdown.variable"
        :label="$t('Markdown Variable')"
        :hint="$t('Variable name of report or finding field (e.g. report.executive_summary, finding.description)')"
        :disabled="props.disabled"
        spellcheck="false"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'chart-create'" class="mb-4">
      <s-select
        v-model="form.chart.chartType"
        :items="['bar (horizontal)', 'bar (vertical)', 'pie', 'doughnut', 'line', 'radar', 'polarArea']"
        :label="$t('Chart Type')"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-text-field
        v-model="form.chart.caption"
        :label="$t('Caption')"
        :disabled="props.disabled"
        spellcheck="false"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'footer-create'">
      <s-text-field
        v-model="form.footer.textLeft"
        :label="$t('Footer Text Left (optional)')"
        spellcheck="false"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-text-field
        v-model="form.footer.textCenter"
        :label="$t('Footer Text Center (optional)')"
        spellcheck="false"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-select
        v-model="form.footer.pageNumberStyle"
        :items="[{value: 'page', title: $t('page')}, {value: 'page-of', title: $t('page / pages')}, {value: 'none', title: $t('no page number')}]"
        :label="$t('Page Number Style')"
        :disabled="props.disabled"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'header-create'">
      <s-select
        v-model="form.header.left"
        :items="[ {value: null, title: $t('none')}, {value: 'text', title: $t('Text')}, {value: 'logo', title: $t('Logo')}]"
        :label="$t('Header Left')"
        :hint="form.header.left === 'logo' ? $t('Logo image must be uploaded in assets as logo.png') : ''"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-select
        v-model="form.header.right"
        :items="[ {value: null, title: $t('none')}, {value: 'text', title: $t('Text')}, {value: 'logo', title: $t('Logo')}]"
        :label="$t('Header Right')"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-text-field
        v-model="form.header.backgroundColor"
        :label="$t('Header background color (optional)')"
        :hint="$t('CSS value: #ff0000 or rgb(255, 0, 0) or red')"
        spellcheck="false"
        class="mb-4"
        :disabled="props.disabled"
      />
    </div>
    <div v-if="form.form === 'toc-create'">
      <s-text-field
        v-model="form.toc.headline"
        :label="$t('Headline')"
        spellcheck="false"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-select
        v-model="form.toc.variant"
        :items="['default', 'compact']"
        :label="$t('ToC Variant')"
        :hint="$t('Choose between some predefined styles')"
        class="mb-4"
        :disabled="props.disabled"
      />
      <s-checkbox
        v-model="form.toc.leader"
        :label="$t('Show dot leader (line of dots) between chapter title and page number')"
        :disabled="props.disabled"
        class="mb-4"
      />
    </div>
    <div v-if="form.form === 'finding-list-create'">
      <s-text-field
        v-model="form.findingList.headline"
        :label="$t('Chapter Headline')"
        :disabled="props.disabled"
        spellcheck="false"
        class="mb-4"
      />
      <s-select
        v-model="form.findingList.headerVariant"
        :items="['default', 'table']"
        :label="$t('Finding List Variant')"
        :hint="$t('Choose between some predefined styles')"
        :disabled="props.disabled"
      />

      <p>
        {{ $t('Markdown fields from the finding field definition will be added to HTML.') }}
        {{ $t('You can add and style the remaining fields afterwards in HTML.') }}
      </p>
    </div>
    <div v-if="form.form === 'page-cover-create'">
      <s-select
        v-model="form.coverPage.background"
        :label="$t('Page Background')"
        :items="[{value: null, title: $t('none')}, {value: 'color', title: $t('Color')}, {value: 'image', title: $t('Image')}]"
        :hint="form.coverPage.background === 'image' ? $t('Image must be uploaded in assets as background.png. The background image can later be customized in CSS code.') : form.coverPage.background === 'color' ? $t('The color can be customized later in CSS code') : ''"
        :disabled="props.disabled"
      />
      <s-checkbox
        v-model="form.coverPage.hideHeader"
        :label="$t('Hide header on page')"
        :disabled="props.disabled"
      />
      <s-checkbox
        v-model="form.coverPage.hideFooter"
        :label="$t('Hide footer on page')"
        :disabled="props.disabled"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { pick } from "lodash-es";
import type { MarkdownEditorMode } from "#imports";
import type { MarkdownProps } from "@/composables/markdown";

const props = defineProps<{
  modelValue: any;
  disabled?: boolean;
} & MarkdownProps>();
const emit = defineEmits<{
  'update:modelValue': [any];
}>();

const localSettings = useLocalSettings();

const markdownProps = computed(() => ({
  ...pick(props, ['disabled', 'lang', 'uploadFile', 'rewriteFileUrlMap', 'referenceItems']),
  spellcheckEnabled: localSettings.designSpellcheckEnabled,
  'onUpdate:spellcheckEnabled': (value: boolean) => { localSettings.designSpellcheckEnabled = value },
  markdownEditorMode: localSettings.designMarkdownEditorMode,
  'onUpdate:markdownEditorMode': (value: MarkdownEditorMode) => { localSettings.designMarkdownEditorMode = value },
}));

const form = ref();
watch(() => props.modelValue, () => {
  if (props.modelValue !== form.value) {
    form.value = props.modelValue;
  }
}, { immediate: true });
watch(form, () => emit('update:modelValue', form.value), { deep: true });
</script>
