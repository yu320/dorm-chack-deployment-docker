<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('records.myRecordsTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('records.viewPastReports') }}</p>
    </div>

    <!-- Records Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.date') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.room') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.status') }}</th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">{{ $t('admin.actions') }}</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="record in records" :key="record.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ new Date(record.created_at).toLocaleDateString() }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ record.room.room_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300': record.status === 'approved',
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300': record.status === 'submitted',
                    'bg-gray-100 text-gray-800 dark:bg-gray-600/50 dark:text-gray-300': record.status === 'pending',
                  }"
                >
                  {{ $t(`inspection.status.${record.status}`) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <NuxtLink :to="`/records/${record.id}`" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300">{{ $t('records.viewDetails') }}</NuxtLink>
              </td>
            </tr>
            <tr v-if="records.length === 0">
              <td colspan="4" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ $t('records.noRecordsFound') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Loading Skeleton -->
    <div v-if="loading" class="text-center py-8">
      <p>{{ $t('loading') }}</p>
    </div>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center">
        <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50">
                <span>{{ $t('pagination.previous') }}</span>
            </button>
            <button v-for="page in totalPages" :key="page" @click="changePage(page)" :class="['relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium', currentPage === page ? 'bg-primary-50 border-primary-500 text-primary-600 dark:bg-gray-900' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700']">
              {{ page }}
            </button>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50">
                <span>{{ $t('pagination.next') }}</span>
            </button>
        </nav>
    </div>

  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';

interface Room {
  room_number: string;
}

interface InspectionRecord {
  id: string;
  created_at: string;
  room: Room;
  status: string;
}

interface PaginatedResponse {
  total: number;
  records: InspectionRecord[];
}


const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const records = ref<InspectionRecord[]>([]);
const loading = ref(true);

// Pagination state
const currentPage = ref(1);
const totalRecords = ref(0);
const recordsPerPage = 10;
const totalPages = computed(() => Math.ceil(totalRecords.value / recordsPerPage));


const fetchRecords = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      skip: ((currentPage.value - 1) * recordsPerPage).toString(),
      limit: recordsPerPage.toString(),
    });
    // The backend automatically returns only the user's own records
    const response = await apiFetch(`/api/v1/inspections/?${params.toString()}`) as PaginatedResponse;
    records.value = response.records;
    totalRecords.value = response.total;
  } catch (error) {
    console.error('Failed to fetch records:', error);
    showSnackbar(t('snackbar.failedToFetchRecords'), 'error');
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchRecords();
  }
};

onMounted(() => {
  fetchRecords();
});
</script>