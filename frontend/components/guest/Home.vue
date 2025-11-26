<template>
  <div class="min-h-[80vh] flex flex-col justify-center items-center">
    <div class="max-w-6xl mx-auto text-center py-20 px-4">
      
      <!-- Hero Section -->
      <div class="relative mb-16">
        <div class="absolute inset-0 bg-gradient-to-r from-primary-500/20 to-purple-500/20 blur-3xl rounded-full opacity-50 -z-10"></div>
        
        <div class="mb-8 inline-block p-6 rounded-full bg-white/50 dark:bg-white/10 backdrop-blur-sm shadow-xl animate-bounce-slow border border-white/20">
          <Icon name="heroicons:home-modern" class="h-20 w-20 text-primary-600 dark:text-primary-400" />
        </div>

        <h1 class="text-6xl md:text-8xl font-black text-transparent bg-clip-text bg-gradient-to-r from-primary-600 via-purple-600 to-primary-600 dark:from-primary-400 dark:via-purple-400 dark:to-primary-400 mb-6 animate-gradient-x">
          {{ $t('welcome') }}
        </h1>
        
        <p class="text-xl md:text-2xl text-gray-600 dark:text-gray-300 max-w-2xl mx-auto mb-10 leading-relaxed">
          The modern solution for dormitory management and inspections.
        </p>

        <div class="flex justify-center gap-6">
          <NuxtLink :to="localePath('/login')" class="btn-primary-lg group relative overflow-hidden px-8 py-4 rounded-full shadow-lg hover:shadow-primary-500/50 transition-all duration-300">
            <span class="relative z-10 flex items-center text-lg font-bold">
              {{ $t('getStarted') }}
              <Icon name="heroicons:arrow-right" class="ml-2 w-6 h-6 group-hover:translate-x-1 transition-transform" />
            </span>
            <div class="absolute inset-0 bg-gradient-to-r from-primary-600 to-purple-600 opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          </NuxtLink>
        </div>
      </div>

      <!-- How it Works Section -->
      <div class="mb-24">
        <h2 class="text-3xl font-bold text-gray-800 dark:text-white mb-12">How it Works</h2>
        <div class="flex flex-col md:flex-row justify-center items-center gap-8 relative">
          <!-- Connecting Line (Desktop) -->
          <div class="hidden md:block absolute top-1/2 left-0 w-full h-1 bg-gray-200 dark:bg-gray-700 -z-10 transform -translate-y-1/2"></div>

          <!-- Step 1 -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 w-64 relative z-10">
            <div class="w-12 h-12 bg-primary-100 dark:bg-primary-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-primary-600 dark:text-primary-400 font-bold text-xl">1</div>
            <h3 class="font-bold text-lg mb-2">Login</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Access your student account securely.</p>
          </div>

          <!-- Step 2 -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 w-64 relative z-10">
            <div class="w-12 h-12 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-purple-600 dark:text-purple-400 font-bold text-xl">2</div>
            <h3 class="font-bold text-lg mb-2">Inspect</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Complete the digital room checklist.</p>
          </div>

          <!-- Step 3 -->
          <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 w-64 relative z-10">
            <div class="w-12 h-12 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center mx-auto mb-4 text-green-600 dark:text-green-400 font-bold text-xl">3</div>
            <h3 class="font-bold text-lg mb-2">Submit</h3>
            <p class="text-sm text-gray-500 dark:text-gray-400">Get instant confirmation and updates.</p>
          </div>
        </div>
      </div>

      <!-- Latest Announcements Section -->
      <div class="text-left mb-16">
        <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-6">最新公告</h2>
        <div v-if="loading" class="text-center py-8">
          <p class="text-gray-500 dark:text-gray-400">載入中...</p>
        </div>
        <div v-else-if="announcements.length === 0" class="text-center py-8">
          <p class="text-gray-500 dark:text-gray-400">目前沒有公告</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-3 gap-6">
          <CommonAnnouncementCard
            v-for="announcement in announcements"
            :key="announcement.id"
            :id="announcement.id"
            :title="announcement.title"
            :date="new Date(announcement.created_at).toLocaleDateString('zh-TW')"
            :tag="announcement.tag"
            :tag-type="announcement.tag_type"
            :content="announcement.content"
          />
        </div>
      </div>

      <!-- Features Grid -->
      <div class="grid grid-cols-1 md:grid-cols-3 gap-8 text-left">
        <GuestFeatureCard 
          icon="heroicons:clipboard-document-check" 
          title="Easy Inspection" 
          description="Complete your room inspection in minutes with our intuitive digital checklist."
          color="green"
          class="hover:-translate-y-2 transition-transform duration-300 hover:shadow-xl"
        />
        <GuestFeatureCard 
          icon="heroicons:archive-box" 
          title="Digital Records" 
          description="Keep track of all your past inspections and room conditions securely."
          color="blue"
          class="hover:-translate-y-2 transition-transform duration-300 hover:shadow-xl"
        />
        <GuestFeatureCard 
          icon="heroicons:bell-alert" 
          title="Instant Updates" 
          description="Receive real-time notifications about your inspection status."
          color="purple"
          class="hover:-translate-y-2 transition-transform duration-300 hover:shadow-xl"
        />
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useAnnouncements } from '~/composables/useAnnouncements';
const localePath = useLocalePath();
const { getAnnouncements } = useAnnouncements();

const announcements = ref([]);
const loading = ref(true);

onMounted(async () => {
  try {
    const response = await getAnnouncements(0, 3); // 獲取前 3 條公告
    announcements.value = response.records;
  } catch (error) {
    console.error('Failed to load announcements:', error);
  } finally {
    loading.value = false;
  }
});
</script>