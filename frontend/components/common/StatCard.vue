<template>
  <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-4">
    <div :class="`p-3 rounded-xl ${colorClasses}`">
      <Icon :name="icon" class="h-8 w-8" />
    </div>
    <div>
      <p class="text-sm text-gray-500 dark:text-gray-400">{{ label }}</p>
      <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ value }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  label: string;
  value: number | string;
  icon: string;
  color: 'blue' | 'indigo' | 'green' | 'red';
}>();

const colorMap = {
  blue: 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400',
  indigo: 'bg-indigo-100 text-indigo-600 dark:bg-indigo-900/30 dark:text-indigo-400',
  green: 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400',
  red: 'bg-red-100 text-red-600 dark:bg-red-900/30 dark:text-red-400'
};

const colorClasses = computed(() => colorMap[props.color] || colorMap.blue);
</script>