<template>
  <div class="space-y-8">
    <div class="flex items-center justify-between">
      <div>
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white">{{ $t('dashboard.adminTitle') }}</h1>
        <p class="text-gray-500 mt-1">{{ $t('dashboard.overview') }}</p>
      </div>
      <div class="text-sm text-gray-500 bg-white dark:bg-gray-800 px-4 py-2 rounded-lg shadow-sm border border-gray-100 dark:border-gray-700">
        {{ new Date().toLocaleDateString() }}
      </div>
    </div>

    <!-- Stats Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <CommonStatCard :label="$t('dashboard.totalStudents')" :value="stats.total_students" icon="heroicons:users" color="blue" />
      <CommonStatCard :label="$t('dashboard.totalRooms')" :value="stats.total_rooms" icon="heroicons:key" color="indigo" />
      <CommonStatCard :label="$t('dashboard.inspectionsToday')" :value="stats.inspections_today" icon="heroicons:clipboard" color="green" />
      <CommonStatCard :label="$t('dashboard.issuesFound')" :value="stats.issues_found" icon="heroicons:exclamation-circle" color="red" />
    </div>

    <!-- Charts Section -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h3 class="text-lg font-bold mb-6">Inspection Pass Rate</h3>
        <div class="h-64 flex items-center justify-center">
           <ChartsPassRatePieChart v-if="passRateData.labels.length" :chartData="passRateData" />
           <p v-else class="text-gray-500">No data available</p>
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 p-6">
        <h3 class="text-lg font-bold mb-6">Top Damage Types</h3>
        <div class="h-64 flex items-center justify-center">
           <ChartsDamageRankingBarChart v-if="damageRankingData.labels.length" :chartData="damageRankingData" />
           <p v-else class="text-gray-500">No data available</p>
        </div>
      </div>
    </div>

    <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
      <!-- Recent Inspections Table -->
      <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700">
        <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-lg font-bold">{{ $t('dashboard.recentInspections') }}</h3>
          <NuxtLink :to="localePath('/admin/inspections')" class="text-primary-600 hover:text-primary-700 text-sm font-medium">
            {{ $t('dashboard.viewAll') }}
          </NuxtLink>
        </div>
        <AdminInspectionTable :data="stats.recent_inspections" />
      </div>

      <!-- Quick Actions List -->
      <AdminQuickActions />
    </div>

    <!-- Latest Announcements Section -->
    <div class="mt-8">
      <div class="flex justify-between items-center mb-6">
        <h3 class="text-2xl font-bold text-gray-800 dark:text-white flex items-center">
          <Icon name="heroicons:megaphone" class="mr-3 text-primary-600" />
          最新公告
        </h3>
        <NuxtLink :to="localePath('/admin/announcements')" class="text-primary-600 hover:text-primary-700 font-medium text-sm">
          管理公告 &rarr;
        </NuxtLink>
      </div>
      
      <div v-if="loadingAnnouncements" class="text-center py-8">
        <p class="text-gray-500 dark:text-gray-400">載入中...</p>
      </div>
      <div v-else-if="announcements.length === 0" class="text-center py-8 bg-white dark:bg-gray-800 rounded-2xl border border-gray-100 dark:border-gray-700">
        <p class="text-gray-500 dark:text-gray-400">目前沒有公告</p>
        <NuxtLink :to="localePath('/admin/announcements')" class="mt-4 inline-block text-primary-600 hover:underline">
          立即新增第一則公告
        </NuxtLink>
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
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue';
const localePath = useLocalePath();
const { getAnnouncements } = useAnnouncements();

const props = defineProps<{
  stats: {
    total_students: number;
    total_rooms: number;
    inspections_today: number;
    issues_found: number;
    recent_inspections: any[];
    charts?: {
      pass_rate: Record<string, number>;
      damage_ranking: Array<{ name: string; count: number }>;
    };
  }
}>();

const announcements = ref([]);
const loadingAnnouncements = ref(true);

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

const passRateData = computed(() => {
  if (!props.stats?.charts?.pass_rate) return { labels: [], datasets: [] };
  
  const labels = Object.keys(props.stats.charts.pass_rate);
  const data = Object.values(props.stats.charts.pass_rate);
  
  return {
    labels,
    datasets: [
      {
        backgroundColor: ['#10B981', '#EF4444', '#F59E0B'],
        data
      }
    ]
  };
});

const damageRankingData = computed(() => {
  if (!props.stats?.charts?.damage_ranking) return { labels: [], datasets: [] };
  
  const labels = props.stats.charts.damage_ranking.map(item => item.name);
  const data = props.stats.charts.damage_ranking.map(item => item.count);
  
  return {
    labels,
    datasets: [
      {
        label: 'Damage Count',
        backgroundColor: '#6366F1',
        data
      }
    ]
  };
});
</script>