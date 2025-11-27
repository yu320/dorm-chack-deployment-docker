<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 py-12 px-4 sm:px-6 lg:px-8 transition-colors duration-300">
    <div class="max-w-3xl mx-auto">
      <NuxtLink :to="localePath('/')" class="inline-flex items-center text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200 mb-8 transition-colors">
        <Icon name="heroicons:arrow-left" class="w-5 h-5 mr-2" />
        返回首頁
      </NuxtLink>

      <div v-if="loading" class="text-center py-20">
        <p class="text-xl text-gray-500 dark:text-gray-400">載入中...</p>
      </div>

      <div v-else-if="announcement" class="bg-white dark:bg-gray-800 rounded-2xl shadow-xl overflow-hidden border border-gray-100 dark:border-gray-700">
        <div class="p-8 md:p-12">
          <div class="flex items-center justify-between mb-6">
            <span :class="`px-4 py-1.5 rounded-full text-sm font-medium ${tagColorClasses}`">
              {{ announcement.tag }}
            </span>
            <span class="text-gray-500 dark:text-gray-400 flex items-center">
              <Icon name="heroicons:calendar" class="w-5 h-5 mr-2" />
              {{ new Date(announcement.created_at).toLocaleDateString('zh-TW') }}
            </span>
          </div>

          <h1 class="text-3xl md:text-4xl font-bold text-gray-900 dark:text-white mb-8 leading-tight">
            {{ displayTitle }}
          </h1>

          <div class="prose prose-lg dark:prose-invert max-w-none text-gray-600 dark:text-gray-300">
            <p class="whitespace-pre-wrap">{{ displayContent }}</p>
          </div>
        </div>
      </div>

      <div v-else class="text-center py-20">
        <p class="text-xl text-gray-500 dark:text-gray-400">找不到此公告</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAnnouncements } from '~/composables/useAnnouncements';
const route = useRoute();
const localePath = useLocalePath();
const { getAnnouncement } = useAnnouncements();
const { locale } = useI18n();

const id = route.params.id as string;
const announcement = ref(null);
const loading = ref(true);

onMounted(async () => {
  try {
    announcement.value = await getAnnouncement(id);
  } catch (error) {
    console.error('Failed to load announcement:', error);
  } finally {
    loading.value = false;
  }
});

const displayTitle = computed(() => {
  if (!announcement.value) return '';
  if (locale.value === 'en' && announcement.value.title_en) return announcement.value.title_en;
  return announcement.value.title;
});

const displayContent = computed(() => {
  if (!announcement.value) return '';
  if (locale.value === 'en' && announcement.value.content_en) return announcement.value.content_en;
  return announcement.value.content;
});

const tagColorClasses = computed(() => {
  const colors = {
    primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  };
  return colors[announcement.value?.tag_type || 'primary'];
});

useHead({
  title: computed(() => announcement.value ? `${displayTitle.value} - 公告` : '公告詳情')
});
</script>
