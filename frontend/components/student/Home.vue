<template>
  <div class="space-y-8">
    <!-- Personalized Greeting -->
    <div class="bg-primary-600 rounded-2xl p-8 text-white shadow-lg">
      <h2 class="text-3xl font-bold mb-2 flex items-center">
        <Icon name="heroicons:sparkles" class="mr-3 text-yellow-300" />
        {{ $t('welcome') }}, {{ user?.username || 'Student' }}!
      </h2>
      <p class="text-white/90 text-lg">Here's what's happening with your dormitory today.</p>
    </div>

    <!-- Latest Announcements Section -->
    <div>
      <h3 class="text-2xl font-bold text-gray-800 dark:text-white mb-6 flex items-center">
        <Icon name="heroicons:megaphone" class="mr-3 text-primary-600" />
        最新公告
      </h3>
      <div v-if="loadingAnnouncements" class="text-center py-8">
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
          :title-en="announcement.title_en"
          :date="new Date(announcement.created_at).toLocaleDateString('zh-TW')"
          :tag="announcement.tag"
          :tag-type="announcement.tag_type"
          :content="announcement.content"
          :content-en="announcement.content_en"
        />
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
      
      <!-- Bed Information Card -->
      <CommonInfoCard :title="$t('index.myBed.title')" icon="heroicons:home" color="blue">
        <div v-if="user?.student?.bed" class="space-y-4">
          <CommonInfoRow :label="$t('index.myBed.building')" :value="user.student.bed.room.building.name" />
          <CommonInfoRow :label="$t('index.myBed.room')" :value="user.student.bed.room.room_number" />
          <CommonInfoRow :label="$t('index.myBed.bed')" :value="user.student.bed.bed_number" />
        </div>
        <CommonEmptyState v-else :message="$t('index.myBed.noBedAssigned')" />
      </CommonInfoCard>

      <!-- Latest Inspection Card -->
      <CommonInfoCard :title="$t('index.latestInspection.title')" icon="heroicons:clipboard-document-check" color="green">
        <div v-if="latestInspection" class="space-y-4">
          <CommonInfoRow :label="$t('index.latestInspection.date')" :value="formatDate(latestInspection.created_at)" />
          <div class="flex justify-between items-center">
            <span class="text-gray-500 dark:text-gray-400">{{ $t('index.latestInspection.status') }}</span>
            <CommonStatusBadge :status="latestInspection.status" />
          </div>
          <NuxtLink :to="localePath(`/records/${latestInspection.id}`)" class="btn-outline-green mt-4 block text-center">
            {{ $t('records.viewDetails') }}
          </NuxtLink>
        </div>
        <CommonEmptyState v-else :message="$t('index.latestInspection.noRecord')" />
      </CommonInfoCard>

      <!-- Quick Actions Grid -->
      <div class="space-y-4">
        <h3 class="text-lg font-bold text-gray-800 dark:text-white flex items-center">
          <Icon name="heroicons:bolt" class="mr-2 text-yellow-500" />
          {{ $t('index.quickActions.title') }}
        </h3>
        <div class="grid grid-cols-1 gap-4">
          <NuxtLink :to="localePath('/inspection/new')" class="group bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all duration-200 flex items-center">
            <div class="bg-primary-100 dark:bg-primary-900/30 p-3 rounded-lg mr-4 group-hover:scale-110 transition-transform">
              <Icon name="heroicons:plus-circle" class="w-6 h-6 text-primary-600 dark:text-primary-400" />
            </div>
            <div>
              <div class="font-semibold text-gray-800 dark:text-white">{{ $t('index.quickActions.newInspection') }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">Start a new room check</div>
            </div>
            <Icon name="heroicons:chevron-right" class="ml-auto w-5 h-5 text-gray-400 group-hover:text-primary-500 transition-colors" />
          </NuxtLink>

          <NuxtLink :to="localePath('/records')" class="group bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all duration-200 flex items-center">
            <div class="bg-purple-100 dark:bg-purple-900/30 p-3 rounded-lg mr-4 group-hover:scale-110 transition-transform">
              <Icon name="heroicons:clock" class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <div class="font-semibold text-gray-800 dark:text-white">{{ $t('records.myRecordsTitle') }}</div>
              <div class="text-xs text-gray-500 dark:text-gray-400">View past history</div>
            </div>
            <Icon name="heroicons:chevron-right" class="ml-auto w-5 h-5 text-gray-400 group-hover:text-purple-500 transition-colors" />
          </NuxtLink>
        </div>
      </div>
      
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';

defineProps<{
  user: any;
  latestInspection: any;
}>();

const { getAnnouncements } = useAnnouncements();
const localePath = useLocalePath();

const announcements = ref([]);
const loadingAnnouncements = ref(true);

const formatDate = (date: string) => new Date(date).toLocaleDateString();

onMounted(async () => {
  try {
    const response = await getAnnouncements(0, 3);
    announcements.value = response.records;
  } catch (error) {
    console.error('Failed to load announcements:', error);
  } finally {
    loadingAnnouncements.value = false;
  }
});
</script>