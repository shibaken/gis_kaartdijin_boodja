<template>
  <div class="card">
    <div v-if="$slots.header" class="card-header">
      <slot name="header"/>
    </div>
    <div class="card-body">
      <slot name="body"/>
    </div>
    <div v-if="$slots.footer" class="card-footer">
      <slot name="footer"/>
    </div>
  </div>
</template>