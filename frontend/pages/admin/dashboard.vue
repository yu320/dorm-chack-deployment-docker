<template>
  <div class="space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('dashboard.adminTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('dashboard.overview') }}</p>
    </div>

    <!-- Loading Skeleton -->
    <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="i in 4" :key="i" class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 animate-pulse">
        <div class="h-6 bg-gray-200 dark:bg-gray-700 rounded w-3/4 mx-auto mb-4"></div>
        <div class="h-10 bg-gray-300 dark:bg-gray-600 rounded w-1/2 mx-auto"></div>
      </div>
    </div>

    <!-- Summary Cards -->
    <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h3 class="text-lg font-medium text-gray-500 dark:text-gray-400 mb-2">{{ $t('dashboard.totalStudents') }}</h3>
        <p class="text-4xl font-bold text-primary-600 dark:text-primary-400">{{ stats.total_students }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h3 class="text-lg font-medium text-gray-500 dark:text-gray-400 mb-2">{{ $t('dashboard.totalRooms') }}</h3>
        <p class="text-4xl font-bold text-primary-600 dark:text-primary-400">{{ stats.total_rooms }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h3 class="text-lg font-medium text-gray-500 dark:text-gray-400 mb-2">{{ $t('dashboard.inspectionsToday') }}</h3>
        <p class="text-4xl font-bold text-primary-600 dark:text-primary-400">{{ stats.inspections_today }}</p>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-md p-6 border border-gray-200 dark:border-gray-700 flex flex-col items-center justify-center text-center transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h3 class="text-lg font-medium text-gray-500 dark:text-gray-400 mb-2">{{ $t('dashboard.issuesFound') }}</h3>
        <p class="text-4xl font-bold text-red-600 dark:text-red-500">{{ stats.issues_found }}</p>
      </div>
    </div>

    <!-- Charts Section -->
    <div v-if="!loading && chartData" class="grid grid-cols-1 lg:grid-cols-2 gap-8">
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('dashboard.inspectionStatus') }}</h2>
        <div class="h-64">
          <PassRatePieChart :chart-data="pieChartData" />
        </div>
      </div>
      <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg p-6 border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
        <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('dashboard.topDamagedItems') }}</h2>
        <div class="h-64">
          <DamageRankingBarChart :chart-data="barChartData" />
        </div>
      </div>
    </div>


    <!-- Recent Activity Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700 transition-all duration-300 hover:shadow-xl hover:-translate-y-1">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white p-6 border-b border-gray-200 dark:border-gray-700">{{ $t('dashboard.recentInspections') }}</h2>
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.room') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.inspector') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.status') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.date') }}</th>
               <th scope="col" class="relative px-6 py-3"><span class="sr-only">{{ $t('admin.actions') }}</span></th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="loading" v-for="i in 5" :key="i" class="animate-pulse">
              <td class="px-6 py-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div></td>
              <td class="px-6 py-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div></td>
              <td class="px-6 py-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div></td>
              <td class="px-6 py-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded"></div></td>
              <td class="px-6 py-4"><div class="h-4 bg-gray-200 dark:bg-gray-700 rounded w-1/2"></div></td>
            </tr>
            <tr v-else-if="stats.recent_inspections.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-gray-500 dark:text-gray-400">{{ $t('admin.noRecordsFound') }}</td>
            </tr>
            <tr v-else v-for="inspection in stats.recent_inspections" :key="inspection.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ inspection.room.room_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ inspection.student.full_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${getStatusClass(inspection.status)}`">
                  {{ $t(`inspection.status.${inspection.status}`) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ new Date(inspection.created_at).toLocaleDateString() }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <NuxtLink :to="`/admin/inspections/${inspection.id}`" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300">{{ $t('records.viewDetails') }}</NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useI18n } from '#imports';
import PassRatePieChart from '~/components/charts/PassRatePieChart.vue';
import DamageRankingBarChart from '~/components/charts/DamageRankingBarChart.vue';

definePageMeta({
  permission: 'view_all_records',
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

const loading = ref(true);
const stats = ref({
  total_students: 0,
  total_rooms: 0,
  inspections_today: 0,
  issues_found: 0,
  recent_inspections: [],
});
const chartData = ref(null);

const fetchDashboardStats = async () => {
  try {
    const response = await apiFetch('/api/v1/admin/dashboard-stats');
    stats.value = response;
  } catch (error) {
    showSnackbar(t('snackbar.failedToLoadData'), 'error');

  }
};

const fetchChartData = async () => {
  try {
    chartData.value = await apiFetch('/api/v1/admin/dashboard-charts');
  } catch (error) {
    showSnackbar(t('snackbar.failedToLoadData'), 'error');

  }
};

const pieChartData = computed(() => {
  if (!chartData.value?.pass_rate) return { labels: [], datasets: [] };
  const labels = Object.keys(chartData.value.pass_rate).map(key => t(`inspection.status.${key}`) || key);
  const data = Object.values(chartData.value.pass_rate);
  return {
    labels,
    datasets: [
      {
        backgroundColor: ['#4ade80', '#facc15', '#f87171', '#60a5fa'], // Green, Yellow, Red, Blue
        data,
      },
    ],
  };
});

const barChartData = computed(() => {
  if (!chartData.value?.damage_ranking) return { labels: [], datasets: [] };
  const labels = chartData.value.damage_ranking.map(item => item.name);
  const data = chartData.value.damage_ranking.map(item => item.count);
  return {
    labels,
    datasets: [
      {
        label: t('dashboard.damageReportsCount'),
        backgroundColor: '#4f46e5', // Indigo
        data,
      },
    ],
  };
});


const getStatusClass = (status: string) => {
  switch (status) {
    case 'completed':
      return 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300';
    case 'in_progress':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300';
    case 'needs_reinspection':
      return 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300';
    case 'submitted':
    default:
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300';
  }
};

onMounted(async () => {
  loading.value = true;
  await Promise.all([
    fetchDashboardStats(),
    fetchChartData(),
  ]);
  loading.value = false;
});
</script>
