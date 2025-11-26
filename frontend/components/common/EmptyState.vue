<template>
  <div class="text-center py-8 text-gray-500">
    <Icon name="heroicons:inbox" class="h-12 w-12 mx-auto text-gray-300 mb-3" />
    {{ message }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  message: string;
}>();
</script>