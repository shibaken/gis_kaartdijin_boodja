<template>
  <div class="table-responsive">
    <table class="table table-bordered table-striped table-hover accordion mb-1">
      <thead>
        <slot name="headers"/>
      </thead>
      <tbody>
        <slot name="data"/>
      </tbody>
    </table>
  </div>
  <slot name="pagination"/>
</template>
