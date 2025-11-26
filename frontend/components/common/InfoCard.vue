<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
    <div :class="`p-4 ${headerColorClasses}`">
      <h3 class="text-lg font-semibold text-white flex items-center">
        <Icon :name="icon" class="h-5 w-5 mr-2" />
        {{ title }}
      </h3>
    </div>
    <div class="p-6">
      <slot />
    </div>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  title: string;
  icon: string;
  color: 'blue' | 'green' | 'purple' | 'red' | string;
}>();

const headerColorClasses = computed(() => {
    const map: Record<string, string> = {
        blue: 'bg-gradient-to-r from-blue-500 to-blue-600',
        green: 'bg-gradient-to-r from-green-500 to-green-600',
        purple: 'bg-gradient-to-r from-purple-500 to-purple-600',
        red: 'bg-gradient-to-r from-red-500 to-red-600',
    };
    return map[props.color] || map.blue;
});
</script>