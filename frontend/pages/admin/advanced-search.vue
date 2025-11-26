<template>
  <div class="p-4 sm:p-6">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.advancedSearch') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ $t('admin.advancedSearchDescription') }}
        </p>

        <!-- Search Form -->
        <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <input
            type="text"
            v-model="searchParams.student_name"
            :placeholder="$t('admin.filterByStudent')"
            class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
          <input
            type="text"
            v-model="searchParams.room_number"
            :placeholder="$t('admin.filterByRoom')"
            class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
          <select v-model="searchParams.status" class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600">
            <option value="">{{ $t('admin.allStatuses') }}</option>
            <option value="submitted">{{ $t('inspection.status.submitted') }}</option>
            <option value="passed">{{ $t('dashboard.passed') }}</option>
            <option value="failed">{{ $t('dashboard.failed') }}</option>
          </select>
          <input
            type="date"
            v-model="searchParams.start_date"
            class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
          <input
            type="date"
            v-model="searchParams.end_date"
            class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600"
          />
          <select v-model="searchParams.item_status" class="w-full px-3 py-2 border border-gray-300 rounded-md dark:bg-gray-700 dark:border-gray-600">
            <option value="">All Item Statuses</option>
            <option value="ok">{{ $t('inspection.status.ok') }}</option>
            <option value="damaged">{{ $t('inspection.status.damaged') }}</option>
          </select>
          <button
            @click="performSearch"
            class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg"
          >
            {{ $t('admin.filter') }}
          </button>
        </div>

        <!-- Results Table -->
        <div class="overflow-x-auto">
          <table class="min-w-full bg-white dark:bg-gray-800">
            <thead>
              <tr>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.recordId') }}</th>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.student') }}</th>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.room') }}</th>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.status') }}</th>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.dateSubmitted') }}</th>
                <th class="py-2 px-4 border-b dark:border-gray-700">{{ $t('admin.actions') }}</th>
              </tr>
            </thead>
            <tbody>
              <tr v-if="loading">
                <td colspan="6" class="text-center py-4">{{ $t('loading') }}</td>
              </tr>
              <tr v-else-if="searchResults.length === 0">
                <td colspan="6" class="text-center py-4">{{ $t('admin.noRecordsFound') }}</td>
              </tr>
              <tr v-for="record in searchResults" :key="record.id">
                <td class="py-2 px-4 border-b dark:border-gray-700">{{ record.id }}</td>
                <td class="py-2 px-4 border-b dark:border-gray-700">{{ record.student?.full_name || 'N/A' }}</td>
                <td class="py-2 px-4 border-b dark:border-gray-700">{{ record.room?.room_number || 'N/A' }}</td>
                <td class="py-2 px-4 border-b dark:border-gray-700">{{ $t('inspection.status.' + record.status) }}</td>
                <td class="py-2 px-4 border-b dark:border-gray-700">{{ new Date(record.created_at).toLocaleString() }}</td>
                <td class="py-2 px-4 border-b dark:border-gray-700">
                  <NuxtLink :to="localePath(`/admin/inspections/${record.id}`)" class="text-primary-600 hover:underline">
                    {{ $t('records.viewDetails') }}
                  </NuxtLink>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import type { InspectionRecord } from '~/types';

definePageMeta({
  permission: 'view_all_records',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const localePath = useLocalePath();

const searchParams = ref({
  student_name: '',
  room_number: '',
  status: '',
  start_date: '',
  end_date: '',
  item_status: '',
});

const searchResults = ref<InspectionRecord[]>([]);
const loading = ref(false);

    const performSearch = async () => {
      loading.value = true;
      try {
        const queryParams = new URLSearchParams();
        if (searchParams.value.student_name) {
          queryParams.append('student_name', searchParams.value.student_name);
        }
        if (searchParams.value.room_number) {
          queryParams.append('room_number', searchParams.value.room_number);
        }
        if (searchParams.value.status) {
          queryParams.append('status', searchParams.value.status);
        }
        if (searchParams.value.start_date) {
          queryParams.append('start_date', searchParams.value.start_date);
        }
        if (searchParams.value.end_date) {
          queryParams.append('end_date', searchParams.value.end_date);
        }
        // item_status is not supported by the current backend endpoint, so it's removed.
        const response = await apiFetch(`/api/v1/inspections/search?${queryParams.toString()}`);
        searchResults.value = response.records || [];
      } catch (error) {
    
        // You might want to show a snackbar error here
      } finally {
        loading.value = false;
      }
    };
    
onMounted(() => {
  performSearch();
});
</script>
