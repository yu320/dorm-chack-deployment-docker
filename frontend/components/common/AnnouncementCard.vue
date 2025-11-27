<template>
  <div class="p-6 bg-white dark:bg-gray-800 rounded-2xl shadow-md border border-gray-100 dark:border-gray-700 hover:shadow-xl transition-all duration-300 group h-full flex flex-col">
    <div class="flex items-center justify-between mb-4">
      <span :class="`px-3 py-1 rounded-full text-xs font-medium ${tagColorClasses}`">
        {{ tag }}
      </span>
      <span class="text-sm text-gray-500 dark:text-gray-400 flex items-center">
        <Icon name="heroicons:calendar" class="w-4 h-4 mr-1" />
        {{ date }}
      </span>
    </div>
    
    <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-3 group-hover:text-primary-600 dark:group-hover:text-primary-400 transition-colors">
      {{ displayTitle }}
    </h3>
    
    <p class="text-gray-600 dark:text-gray-400 line-clamp-3 mb-6 flex-grow">
      {{ displayContent }}
    </p>
    
    <NuxtLink :to="localePath(`/announcements/${id}`)" class="flex items-center text-primary-600 dark:text-primary-400 font-medium text-sm group-hover:translate-x-1 transition-transform mt-auto inline-flex">
      閱讀更多
      <Icon name="heroicons:arrow-right" class="w-4 h-4 ml-1" />
    </NuxtLink>
  </div>
</template>

<script setup lang="ts">
const props = defineProps<{
  id: string | number;
  title: string;
  titleEn?: string;
  date: string;
  tag: string;
  tagType?: 'primary' | 'success' | 'warning' | 'danger' | 'info';
  content: string;
  contentEn?: string;
}>();

const localePath = useLocalePath();
const { locale } = useI18n();

const displayTitle = computed(() => {
  if (locale.value === 'en' && props.titleEn) return props.titleEn;
  return props.title;
});

const displayContent = computed(() => {
  if (locale.value === 'en' && props.contentEn) return props.contentEn;
  return props.content;
});

const tagColorClasses = computed(() => {
  const colors = {
    primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  };
  return colors[props.tagType || 'primary'];
});
</script>
