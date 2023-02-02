<script lang="ts" setup>
  import { onMounted, ref, Ref } from "vue";
  import Card from "../widgets/Card.vue";
  import { Metadata } from "../../providers/relatedEntityProvider.api";
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { NavigationEmits } from "../viewState.api";
  import { LayerSubmission } from "../../providers/layerSubmissionProvider.api";
  import { layerSubmissionProvider } from "../../providers/layerSubmissionProvider";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  interface NavEmits extends NavigationEmits {}
  const emit = defineEmits<NavEmits>();

  const metadata: Ref<Metadata | undefined> = ref();
  const activeLayer: Ref<LayerSubmission | undefined> = ref();

  onMounted(async () => {
    metadata.value = props.entry.metadata
    activeLayer.value = await layerSubmissionProvider.fetchLayerSubmission(props.entry.activeLayer);
  });
</script>

<template>
  <card>
    <template #header>
      <h4>Metadata Definition - {{ metadata?.id ? "Edit" : "Add" }}</h4>
    </template>
    <template #body>
      <ol class="list-group list-group-flush">
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="small fw-bold">Create Datetime</div>
            {{ entry.createdAt }}
          </div>
        </li>
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="small fw-bold">Latest Update</div>
            {{ entry.updatedAt }}
          </div>
        </li>
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="small fw-bold">Name</div>
            {{ metadata?.name }}
          </div>
        </li>
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="small fw-bold">Geoserver system filename</div>
            {{ activeLayer?.file }}
          </div>
        </li>
        <li class="list-group-item d-flex justify-content-between align-items-start">
          <div class="ms-2 me-auto">
            <div class="small fw-bold">Editors</div>
            <ul v-if="entry.editors.length > 0" class="list-group">
              <li v-for="editor in entry.editors" class="list-group-item">{{ editor.username }}</li>
            </ul>
          </div>
        </li>
      </ol>
    </template>
  </card>
</template>

<style lang="scss" scoped>
  ul {
    width: min-content;
  }
</style>
