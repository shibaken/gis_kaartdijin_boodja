<script lang="ts" setup>
  import { CatalogueEntry } from "../../providers/catalogueEntryProvider.api";
  import { relatedEntityProvider } from "../../providers/RelatedEntityProvider";
  import Accordion from "../widgets/Accordion.vue";
  import AttributeDatatable from "../dataTable/AttributeDatatable.vue";
  import { onMounted } from "vue";
  import { useAttributeStore } from "../../stores/AttributeStore";
  import { storeToRefs } from "pinia";
  import NotificationsCard from "../widgets/NotificationsCard.vue";

  const props = defineProps<{
    entry: CatalogueEntry
  }>();

  const attributeStore = useAttributeStore();
  const { attributes } = storeToRefs(attributeStore);
  const { setAttributes } = attributeStore;

  onMounted(async () => {
    setAttributes(await relatedEntityProvider.fetchAttributes([props.entry.id]));
  });
</script>

<template>
  <accordion id-prefix="attributeTable" header-text="Attribute Table Definition" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <attribute-datatable :attributes="attributes"/>
      </div>
    </template>
  </accordion>
</template>