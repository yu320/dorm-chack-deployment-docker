<template>
  <div class="p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 hover:shadow-xl transition-shadow duration-300">
    <div :class="`w-12 h-12 ${colorClasses} rounded-xl flex items-center justify-center mb-4`">
      <Icon :name="icon" class="h-6 w-6" />
    </div>
    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-2">{{ title }}</h3>
    <p class="text-gray-600 dark:text-gray-400">{{ description }}</p>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  icon: string;
  title: string;
  description: string;
  color: string;
}>();

const colorClasses = computed(() => {
  const map: Record<string, string> = {
    blue: 'bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400',
    green: 'bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400',
    purple: 'bg-purple-100 dark:bg-purple-900/30 text-purple-600 dark:text-purple-400',
    red: 'bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400',
  };
  return map[props.color] || map.blue;
});
</script>