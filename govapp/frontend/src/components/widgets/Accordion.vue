<script lang="ts" setup>
  defineProps<{
    idPrefix: string;
    headerText: string;
  }>();
</script>

<template>
  <div :id="`${idPrefix}Accordion`" class="accordion">
    <div class="accordion-item">
      <h2 :id="`${idPrefix}HeadingFilter`" class="accordion-header">
        <button class="accordion-button" type="button" data-bs-toggle="collapse" :data-bs-target="`#${idPrefix}Collapse`" aria-expanded="true" :aria-controls="`${idPrefix}Collapse`">
          {{ headerText }}
        </button>
      </h2>
      <div :id="`${idPrefix}Collapse`" class="accordion-collapse collapse show" :aria-labelledby="`${idPrefix}HeadingFilter`" :data-bs-parent="`#${idPrefix}Accordion`">
        <div class="accordion-body">
          <slot name="body"/>
        </div>
      </div>
    </div>
  </div>
</template>