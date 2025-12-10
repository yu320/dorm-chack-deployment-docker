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
        <input type="text" v-model="filters.student_name" :placeholder="$t('admin.filterByStudent')" class="input-field">
        <input type="text" v-model="filters.room_number" :placeholder="$t('admin.filterByRoom')" class="input-field">
        <select v-model="filters.status" class="input-field">
          <option value="">{{ $t('admin.allStatuses') }}</option>
          <option v-for="status in availableStatuses" :key="status" :value="status">{{ status }}</option>
        </select>
        <input type="date" v-model="filters.start_date" class="input-field">
        <input type="date" v-model="filters.end_date" class="input-field">
      </div>
        <div class="mt-4 flex justify-between items-center">
            <!-- Batch Actions -->
            <div v-if="selectedRecords.length > 0" class="flex items-center space-x-2">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                    {{ $t('common.selected', { count: selectedRecords.length }) }}
                </span>
                <button 
                    v-permission="'inspections:delete'"
                    @click="handleBatchDelete" 
                    class="btn-danger text-sm py-1 px-3"
                >
                    {{ $t('admin.deleteSelected') }}
                </button>
            </div>
            <div v-else></div> <!-- Spacer -->

            <button @click="handleSearch" class="btn-primary">
                {{ $t('common.search') }}
            </button>
        </div>
    </div>

    <!-- Data Table -->
    <DataTable
      :columns="tableColumns"
      :data="records"
      :loading="isLoading"
      :current-page="currentPage"
      :total-pages="totalPages"
      :selectable="true"
      :actions="true"
      v-model="selectedRecords"
      @page-change="changePage"
    >
        <template #cell-status="{ item }">
            <span 
                class="px-2 inline-flex text-xs leading-5 font-semibold rounded-full"
                :class="{
                'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300': item.status === 'approved',
                'bg-yellow-100 text-yellow-800 dark:bg-yellow-800/30 dark:text-yellow-300': item.status === 'submitted',
                'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300': item.status === 'pending',
                }"
            >
                {{ item.status }}
            </span>
        </template>
        <template #cell-created_at="{ item }">
            {{ new Date(item.created_at).toLocaleString() }}
        </template>
        <template #cell-student="{ item }">
            {{ item.student?.full_name }} ({{ item.student?.student_id_number }})
        </template>
        <template #cell-room="{ item }">
             {{ item.room?.building?.name }} - {{ item.room?.room_number }}
        </template>
        <template #actions="{ item }">
            <button @click="viewRecord(item.id)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 font-medium mr-3">
                {{ $t('admin.view') }}
            </button>
            <button v-permission="'inspections:delete'" @click="handleDelete(item.id)" class="text-red-600 dark:text-red-400 hover:text-red-900 dark:hover:text-red-300 font-medium">
                {{ $t('admin.delete') }}
            </button>
        </template>
    </DataTable>

    <!-- Delete Confirmation Modal -->
    <Modal
      :is-open="isDeleteModalOpen"
      :title="$t('admin.confirmDelete')"
      :show-confirm="true"
      :confirm-text="$t('admin.delete')"
      :close-text="$t('common.cancel')"
      @close="closeDeleteModal"
      @confirm="confirmDelete"
    >
      <p class="text-sm text-gray-500 dark:text-gray-400">
        {{ $t('admin.deleteRecordConfirmation') }}
      </p>
    </Modal>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useRouter } from 'vue-router'
import { useI18n } from 'vue-i18n'
import { useSnackbar } from '~/composables/useSnackbar'
import { useInspections } from '~/composables/useInspections'
import { useAuth } from '~/composables/useAuth'
import DataTable from '~/components/common/DataTable.vue'
import Modal from '~/components/common/Modal.vue'
import type { InspectionRecord, PaginatedResponse } from '~/types'

definePageMeta({
  permission: 'view_all_records'
})

const { t } = useI18n()
const { apiFetch, hasPermission } = useAuth() // Add hasPermission
const { showSnackbar } = useSnackbar()
const { searchInspections, deleteInspection, isLoading } = useInspections() // Add deleteInspection
const router = useRouter()

const records = ref<InspectionRecord[]>([])
const availableStatuses = ['pending', 'submitted', 'approved']

// Filters
const filters = ref({
    student_name: '',
    room_number: '',
    status: '',
    start_date: '',
    end_date: ''
})

// Pagination
const currentPage = ref(1)
const totalRecords = ref(0)
const recordsPerPage = 10
const totalPages = computed(() => Math.ceil(totalRecords.value / recordsPerPage))

// Delete Modal State
const isDeleteModalOpen = ref(false)
const recordToDelete = ref<string | null>(null)
const isBatchDelete = ref(false) // Track if it's a batch delete
const selectedRecords = ref<string[]>([]) // Track selected record IDs

// Table Columns
const tableColumns = [
  { key: 'id', label: t('admin.recordId'), class: 'text-left' },
  { key: 'student', label: t('admin.student'), class: 'text-left' },
  { key: 'room', label: t('admin.room'), class: 'text-left' },
  { key: 'status', label: t('admin.status'), class: 'text-left' },
  { key: 'created_at', label: t('admin.dateSubmitted'), class: 'text-left' },
]

const fetchRecords = async () => {
  try {
    const params = {
        ...filters.value,
        skip: (currentPage.value - 1) * recordsPerPage,
        limit: recordsPerPage,
        // Convert dates to ISO if needed
        start_date: filters.value.start_date ? new Date(filters.value.start_date).toISOString() : undefined,
        end_date: filters.value.end_date ? new Date(filters.value.end_date).toISOString() : undefined
    }
    
    const response = await searchInspections(params)
    records.value = response.records
    totalRecords.value = response.total
    // Clear selection on page change or refresh if desired, but keeping it is also fine.
    // selectedRecords.value = [] 
  } catch (e) {
    showSnackbar({ message: t('snackbar.failedToFetchRecords'), type: 'error' })
  }
}

const handleSearch = () => {
    currentPage.value = 1
    fetchRecords()
}

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page
    fetchRecords()
  }
}

const viewRecord = (recordId: string) => {
  router.push(`/admin/inspections/${recordId}`) // Corrected path for admin view
}

const handleDelete = (id: string) => {
  recordToDelete.value = id
  isBatchDelete.value = false
  isDeleteModalOpen.value = true
}

const handleBatchDelete = () => {
    if (selectedRecords.value.length === 0) return
    isBatchDelete.value = true
    isDeleteModalOpen.value = true
}

const confirmDelete = async () => {
  try {
    if (isBatchDelete.value) {
        // Execute batch delete
        // We can loop or add a batch delete API. Loop for now to reuse deleteInspection
        // Ideally backend should support batch delete.
        const promises = selectedRecords.value.map(id => deleteInspection(id))
        await Promise.all(promises)
        showSnackbar({ message: t('snackbar.recordsDeleted', { count: selectedRecords.value.length }), type: 'success' })
        selectedRecords.value = [] // Clear selection
    } else {
        if (!recordToDelete.value) return
        await deleteInspection(recordToDelete.value)
        showSnackbar({ message: t('snackbar.recordDeleted'), type: 'success' })
    }
    await fetchRecords()
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToDeleteRecord'), type: 'error' })
  } finally {
    isDeleteModalOpen.value = false
    recordToDelete.value = null
    isBatchDelete.value = false
  }
}

const closeDeleteModal = () => {
  isDeleteModalOpen.value = false
  recordToDelete.value = null
  isBatchDelete.value = false
}

onMounted(fetchRecords)
</script>

<style scoped>
.input-field {
  @apply block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500;
}
</style>
