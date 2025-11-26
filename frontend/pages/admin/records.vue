<template>
  <div class="max-w-7xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.allInspectionRecords') }}</h1>
    </div>

    <!-- Filter Section -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.filters') }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
        <input type="text" v-model="studentNameFilter" :placeholder="$t('admin.filterByStudent')" class="input-field">
        <input type="text" v-model="roomNumberFilter" :placeholder="$t('admin.filterByRoom')" class="input-field">
        <select v-model="statusFilter" class="input-field">
          <option value="">{{ $t('admin.allStatuses') }}</option>
          <option v-for="status in availableStatuses" :key="status" :value="status">{{ status }}</option>
        </select>
        <input type="date" v-model="startDateFilter" class="input-field">
        <input type="date" v-model="endDateFilter" class="input-field">
      </div>
      <div class="flex justify-end mt-4">
        <button @click="fetchRecords" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
          {{ $t('admin.filter') }}
        </button>
      </div>
    </div>

    <!-- Records Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th v-for="header in headers" :key="header.key" scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t(header.title) }}</th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-if="loading">
              <td :colspan="headers.length" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ $t('loading') }}</td>
            </tr>
            <tr v-else-if="records.length === 0">
              <td :colspan="headers.length" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ $t('admin.noRecordsFound') }}</td>
            </tr>
            <tr v-for="record in records" :key="record.id" @click="viewRecord(record.id)" class="hover:bg-gray-50 dark:hover:bg-gray-700 cursor-pointer">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ record.id }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ record.student?.full_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ record.room.room_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                  :class="{
                    'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300': record.status === 'approved',
                    'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/30 dark:text-yellow-300': record.status === 'submitted',
                    'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300': record.status === 'pending',
                  }"
                >
                  {{ record.status }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ new Date(record.created_at).toLocaleString() }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useI18n } from 'vue-i18n'
import { useSnackbar } from '~/composables/useSnackbar'

definePageMeta({
  permission: 'view_all_records'
})



const { t } = useI18n()
const { apiFetch } = useAuth()
const { showSnackbar } = useSnackbar()
const router = useRouter()

const loading = ref(true)
const records = ref<any[]>([])
const headers = [
  { title: 'admin.recordId', key: 'id' },
  { title: 'admin.student', key: 'student.full_name' },
  { title: 'admin.room', key: 'room.room_number' },
  { title: 'admin.status', key: 'status' },
  { title: 'admin.dateSubmitted', key: 'created_at' },
]

const studentNameFilter = ref('')
const roomNumberFilter = ref('')
const statusFilter = ref('')
const startDateFilter = ref('')
const endDateFilter = ref('')
const availableStatuses = ['pending', 'submitted', 'approved']

const fetchRecords = async () => {
  loading.value = true
  try {
    const params = new URLSearchParams()
    if (studentNameFilter.value) params.append('full_name', studentNameFilter.value)
    if (roomNumberFilter.value) params.append('room_number', roomNumberFilter.value)
    if (statusFilter.value) params.append('status', statusFilter.value)
    if (startDateFilter.value) params.append('start_date', new Date(startDateFilter.value).toISOString())
    if (endDateFilter.value) params.append('end_date', new Date(endDateFilter.value).toISOString())
    
    const response = await apiFetch(`/api/v1/inspections/?${params.toString()}`)
    records.value = response.records as any[]
  } catch (e) {
    
    showSnackbar(t('snackbar.failedToFetchRecords'), 'error')
  } finally {
    loading.value = false
  }
}

const viewRecord = (recordId: string) => {
  router.push(`/records/${recordId}`)
}

onMounted(fetchRecords)
</script>

<style scoped>
.input-field {
  @apply block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500;
}
</style>
