import { defineStore } from "pinia";
import { Attribute } from "../providers/relatedEntityProvider.api";
import { ref, Ref } from "vue";

export const useAttributeStore = defineStore("attribute",  () => {
  const attributes: Ref<Attribute[]> = ref([]);

  function setAttributes (newAttributes: Array<Attribute>) {
    attributes.value = newAttributes;
  }

  return { attributes, setAttributes };
});
