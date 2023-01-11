<script lang="ts" setup>
  import { LayerSubscription } from "../../providers/layerSubscriptionProvider.api";
  import FormInput from "../widgets/FormInput.vue";
  import Accordion from "../widgets/Accordion.vue";

  defineProps<{
    subscription: LayerSubscription
  }>();
</script>

<template>
  <accordion id-prefix="details" header-text="Details" class="mt-4">
    <template #body>
      <div class="form d-flex gap-3 flex-column">
        <form-input field="name" name="Name" :value="subscription?.name" type="text" :readonly="true"/>
        <form-input field="url" name="Webservice URL" :value="subscription?.url" type="text"
                    :readonly="true"/>
        <form-input field="frequency" name="Refresh Frequency" :value="subscription?.frequency" type="text"
                    :readonly="true"/>
      </div>
    </template>
  </accordion>
</template>