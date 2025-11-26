<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('inspection.detailsTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('admin.manageInspections') }}</p>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.filterInspections') }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input type="date" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <input type="text" :placeholder="$t('admin.filterByStudent')" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <input type="text" :placeholder="$t('admin.filterByRoom')" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <select class="form-select block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
          <option value="">{{ $t('admin.allStatuses') }}</option>
          <option value="passed">{{ $t('dashboard.passed') }}</option>
          <option value="failed">{{ $t('dashboard.failed') }}</option>
        </select>
      </div>
    </div>

    <!-- Records Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.date') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('inspection.student') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.room') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.status') }}</th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">{{ $t('admin.actions') }}</span>
              </th>
            </tr>
          </thead>
          <tbody v-if="loading" class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr>
              <td colspan="5" class="text-center py-8">
                <p>Loading...</p>
              </td>
            </tr>
          </tbody>
          <tbody v-else class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="inspection in inspections" :key="inspection.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ new Date(inspection.created_at).toLocaleDateString() }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ inspection.student.full_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ inspection.room.room_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full" :class="{ 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300': inspection.status === 'approved', 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300': inspection.status === 'submitted', 'bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300': inspection.status === 'pending' }">
                  {{ $t('inspection.status.' + inspection.status) }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <NuxtLink :to="`/admin/inspections/${inspection.id}`" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300">{{ $t('records.viewDetails') }}</NuxtLink>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
    
    <!-- Pagination -->
    <div class="mt-6 flex justify-center">
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
import { ref, onMounted, computed } from 'vue'
import { useI18n } from 'vue-i18n'
import { useAuth } from '~/composables/useAuth'
import { useSnackbar } from '~/composables/useSnackbar'

definePageMeta({
  permission: 'inspections:view',
});

const { t } = useI18n()
const { apiFetch } = useAuth()
const { showSnackbar } = useSnackbar()

const inspections = ref([])
const loading = ref(true)
const currentPage = ref(1)
const totalInspections = ref(0)
const inspectionsPerPage = 10

const totalPages = computed(() => Math.ceil(totalInspections.value / inspectionsPerPage))

const fetchInspections = async () => {
  loading.value = true
  try {
    // Define a type for the expected response to improve type safety
    type PaginatedResponse = {
      total: number;
      records: any[]; // Consider defining a more specific type for inspection records
    };

    const response = await apiFetch(`/api/v1/inspections/search?skip=${(currentPage.value - 1) * inspectionsPerPage}&limit=${inspectionsPerPage}`) as PaginatedResponse;
    
    console.log('Inspections API Response:', response); // Debug log

    if (response && Array.isArray(response.records)) {
      inspections.value = response.records;
      totalInspections.value = response.total;
    } else {
      console.warn('Unexpected response format for inspections:', response);
      inspections.value = [];
      totalInspections.value = 0;
    }
  } catch (error) {
    console.error('Error fetching inspections:', error); // Debug log
    showSnackbar({ message: t('snackbar.failedToLoadInspections'), type: 'error' })
    // Reset data on error to avoid inconsistent state
    inspections.value = [];
    totalInspections.value = 0;
  } finally {
    loading.value = false
  }
}

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page
    fetchInspections()
  }
}

onMounted(fetchInspections)
</script>