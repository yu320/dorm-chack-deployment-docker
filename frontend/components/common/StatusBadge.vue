<template>
  <span :class="`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide ${colorClass}`">
    {{ $t(`inspection.status.${status}`) }}
  </span>
</template>

<script setup lang="ts">
const props = defineProps<{ status: string }>();

const colorClass = computed(() => {
  switch (props.status) {
    case 'approved':
      return 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300';
    case 'submitted':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300';
    case 'pending':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
});
</script>