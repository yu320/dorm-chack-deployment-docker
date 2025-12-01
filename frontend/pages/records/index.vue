<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('records.myRecordsTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('records.viewPastReports') }}</p>
    </div>

    <!-- Records Table -->
    <DataTable
      :columns="tableColumns"
      :data="records"
      :loading="isLoading"
      :actions="true"
      :empty-text="$t('records.noRecordsFound')"
    >
        <template #created_at="{ item }">
            {{ new Date(item.created_at).toLocaleDateString() }}
        </template>
        <template #room="{ item }">
            {{ item.room.room_number }}
        </template>
        <template #status="{ item }">
            <span 
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="{
                'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300': item.status === 'approved',
                'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300': item.status === 'submitted',
                'bg-gray-100 text-gray-800 dark:bg-gray-600/50 dark:text-gray-300': item.status === 'pending',
                }"
            >
                {{ $t(`inspection.status.${item.status}`) }}
            </span>
        </template>
        <template #actions="{ item }">
            <NuxtLink :to="`/records/${item.id}`" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 font-medium">
                {{ $t('records.viewDetails') }}
            </NuxtLink>
        </template>
    </DataTable>

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
import { useSnackbar } from '~/composables/useSnackbar';
import { useInspections } from '~/composables/useInspections';
import DataTable from '~/components/common/DataTable.vue';
import type { InspectionRecord, PaginatedResponse } from '~/types';

const { t } = useI18n();
const { showSnackbar } = useSnackbar();
const { getInspections, isLoading } = useInspections();

const records = ref<InspectionRecord[]>([]);

// Pagination state
const currentPage = ref(1);
const totalRecords = ref(0);
const recordsPerPage = 10;
const totalPages = computed(() => Math.ceil(totalRecords.value / recordsPerPage));

// Table Columns
const tableColumns = [
  { key: 'created_at', label: t('dashboard.date'), class: 'text-left' },
  { key: 'room', label: t('dashboard.room'), class: 'text-left' },
  { key: 'status', label: t('dashboard.status'), class: 'text-left' },
];

const fetchRecordsData = async () => {
  try {
    const params = {
      skip: (currentPage.value - 1) * recordsPerPage,
      limit: recordsPerPage,
    };
    const response = await getInspections(params) as PaginatedResponse<InspectionRecord>;
    records.value = response.records;
    totalRecords.value = response.total;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToFetchRecords'), type: 'error' });
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchRecordsData();
  }
};

onMounted(() => {
  fetchRecordsData();
});
</script>