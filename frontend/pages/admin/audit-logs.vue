<template>
  <div class="max-w-7xl mx-auto space-y-6 p-4 sm:p-6 lg:p-8">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ $t('admin.auditLogsTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">{{ $t('admin.auditLogsDescription') }}</p>
    </div>

    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <div class="grid grid-cols-1 md:grid-cols-4 gap-4">
        <input v-model="filters.start_date" type="date" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <input v-model="filters.end_date" type="date" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <input v-model="filters.action" type="text" :placeholder="$t('admin.filterByAction')" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
        <input v-model="filters.resource_type" type="text" :placeholder="$t('admin.filterByResourceType')" class="form-input block w-full border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm focus:border-primary-500 focus:ring-primary-500">
      </div>
      <div class="mt-4 flex justify-end">
        <button @click="fetchLogs" class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg">
          {{ $t('admin.applyFilters') }}
        </button>
      </div>
    </div>

    <!-- Logs Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.date') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.user') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.action') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.resourceType') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.details') }}</th>
            </tr>
          </thead>
          <tbody v-if="loading" class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr>
              <td colspan="5" class="text-center py-8">
                <p>{{ $t('loading') }}</p>
              </td>
            </tr>
          </tbody>
          <tbody v-else class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white">{{ new Date(log.created_at).toLocaleString() }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ log.user ? log.user.username : 'System' }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ log.action }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ log.resource_type }}</td>
              <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                <button v-if="log.details" @click="openDetailsModal(log)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300">
                  {{ $t('admin.viewDetails') }}
                </button>
                <span v-else>-</span>
              </td>
            </tr>
            <tr v-if="logs.length === 0">
              <td colspan="5" class="text-center py-8 text-gray-500 dark:text-gray-400">
                {{ $t('admin.noLogsFound') }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Pagination -->
    <div class="flex justify-center mt-6">
       <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
            <button @click="changePage(currentPage - 1)" :disabled="currentPage === 1" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50">
                <span>{{ $t('pagination.previous') }}</span>
            </button>
            <button @click="changePage(currentPage + 1)" :disabled="currentPage === totalPages" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50">
                <span>{{ $t('pagination.next') }}</span>
            </button>
        </nav>
    </div>


    <!-- Details Modal -->
    <Modal :isOpen="showDetailsModal" :title="$t('admin.logDetails')" :closeText="$t('close')" @close="closeDetailsModal">
      <div class="bg-gray-50 dark:bg-gray-900 p-4 rounded-md overflow-auto max-h-96">
        <pre class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap">{{ formattedDetails }}</pre>
      </div>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted, computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import Modal from '~/components/common/Modal.vue';
import DataTable from '~/components/common/DataTable.vue'; // Explicit import
import { useI18n } from '#imports';

definePageMeta({
  permission: 'audit_logs:view',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const logs = ref<any[]>([]);
const loading = ref(false);
const currentPage = ref(1);
const totalLogs = ref(0);
const limit = 20;
const totalPages = computed(() => Math.ceil(totalLogs.value / limit));

const showDetailsModal = ref(false);
const selectedLog = ref<any>(null);
const formattedDetails = computed(() => {
  if (!selectedLog.value || !selectedLog.value.details) return '';
  return JSON.stringify(selectedLog.value.details, null, 2);
});

const openDetailsModal = (log: any) => {
  selectedLog.value = log;
  showDetailsModal.value = true;
};

const closeDetailsModal = () => {
  showDetailsModal.value = false;
  selectedLog.value = null;
};

const filters = reactive({
  start_date: '',
  end_date: '',
  action: '',
  resource_type: '',
});

const fetchLogs = async () => {
  loading.value = true;
  try {
    const query = new URLSearchParams({
      skip: ((currentPage.value - 1) * limit).toString(),
      limit: limit.toString(),
      ...filters
    });
    
    // Remove empty filters
    for (const [key, value] of Object.entries(filters)) {
        if (!value) query.delete(key);
    }

    const response = await apiFetch(`/api/v1/audit-logs/?${query.toString()}`) as any;
    logs.value = response.records || [];
    totalLogs.value = response.total || 0;
  } catch (error) {
    console.error('Failed to fetch audit logs:', error);
    showSnackbar({ message: t('snackbar.failedToLoadLogs'), type: 'error' });
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  if (page < 1 || page > totalPages.value) return;
  currentPage.value = page;
  fetchLogs();
};

onMounted(fetchLogs);
</script>
