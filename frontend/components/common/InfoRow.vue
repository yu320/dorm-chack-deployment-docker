<template>
  <div class="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-2 last:border-0 last:pb-0">
    <span class="text-gray-500 dark:text-gray-400">{{ label }}</span>
    <span class="font-medium text-gray-800 dark:text-white">{{ value }}</span>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  label: string;
  value: string | number;
}>();
</script>