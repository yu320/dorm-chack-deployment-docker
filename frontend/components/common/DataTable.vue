<template>
  <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
    <div class="overflow-x-auto">
      <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
        <thead class="bg-gray-50 dark:bg-gray-700/50">
          <tr>
            <th v-if="selectable" scope="col" class="px-6 py-3 text-left">
              <input 
                type="checkbox" 
                class="form-checkbox h-4 w-4 text-primary-600 transition duration-150 ease-in-out"
                :checked="isAllSelected"
                :indeterminate="isIndeterminate"
                @change="toggleSelectAll"
              />
            </th>
            <th 
              v-for="col in columns" 
              :key="col.key"
              scope="col" 
              class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider"
              :class="col.class"
            >
              <slot :name="'header-' + col.key" :label="col.label">
                {{ col.label }}
              </slot>
            </th>
            <th v-if="actions || $slots.actions" scope="col" class="relative px-6 py-3"><span class="sr-only">操作</span></th>
          </tr>
        </thead>
        <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
          <tr v-if="loading">
            <td :colspan="columns.length + (selectable ? 1 : 0) + ((actions || $slots.actions) ? 1 : 0)" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
              載入中...
            </td>
          </tr>
          <template v-else>
            <tr v-for="(item, index) in data" :key="item.id || index" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td v-if="selectable" class="px-6 py-4 whitespace-nowrap">
                <input 
                  type="checkbox" 
                  class="form-checkbox h-4 w-4 text-primary-600 transition duration-150 ease-in-out"
                  :checked="isSelected(item)"
                  @change="toggleSelect(item)"
                />
              </td>
              <td 
                v-for="col in columns" 
                :key="col.key" 
                class="px-6 py-4 whitespace-nowrap text-sm text-gray-900 dark:text-white"
                :class="col.cellClass"
              >
                <!-- Slot for custom cell content -->
                <slot :name="'cell-' + col.key" :item="item" :value="item[col.key]">
                  {{ item[col.key] }}
                </slot>
              </td>
              <td v-if="actions || $slots.actions" class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <slot name="actions" :item="item"></slot>
              </td>
            </tr>
            <tr v-if="!data || data.length === 0">
              <td :colspan="columns.length + (selectable ? 1 : 0) + ((actions || $slots.actions) ? 1 : 0)" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">
                {{ emptyText }}
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
    
    <!-- Pagination (Optional, if handled by parent) -->
    <div v-if="totalPages > 1" class="bg-white dark:bg-gray-800 px-4 py-3 flex items-center justify-between border-t border-gray-200 dark:border-gray-700 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
            <button @click="$emit('page-change', currentPage - 1)" :disabled="currentPage === 1" class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                Previous
            </button>
            <button @click="$emit('page-change', currentPage + 1)" :disabled="currentPage === totalPages" class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50">
                Next
            </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
            <div>
                <p class="text-sm text-gray-700 dark:text-gray-300">
                    Page <span class="font-medium">{{ currentPage }}</span> of <span class="font-medium">{{ totalPages }}</span>
                </p>
            </div>
            <div>
                <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
                    <button @click="$emit('page-change', currentPage - 1)" :disabled="currentPage === 1" class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600">
                        <span class="sr-only">Previous</span>
                        <!-- Heroicon name: solid/chevron-left -->
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                        </svg>
                    </button>
                    <button @click="$emit('page-change', currentPage + 1)" :disabled="currentPage === totalPages" class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white dark:bg-gray-700 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-600">
                        <span class="sr-only">Next</span>
                        <!-- Heroicon name: solid/chevron-right -->
                        <svg class="h-5 w-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
                            <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                        </svg>
                    </button>
                </nav>
            </div>
        </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, PropType } from 'vue'

export interface Column {
  key: string
  label: string
  class?: string
  cellClass?: string
}

const props = defineProps({
  columns: {
    type: Array as PropType<Column[]>,
    required: true
  },
  data: {
    type: Array as PropType<any[]>,
    required: true
  },
  loading: {
    type: Boolean,
    default: false
  },
  actions: {
    type: Boolean,
    default: false
  },
  emptyText: {
    type: String,
    default: '目前沒有資料'
  },
  selectable: {
    type: Boolean,
    default: false
  },
  modelValue: {
    type: Array as PropType<any[]>,
    default: () => []
  },
  currentPage: {
    type: Number,
    default: 1
  },
  totalPages: {
    type: Number,
    default: 1
  }
})

const emit = defineEmits(['update:modelValue', 'page-change'])

// Selection Logic
const selectedIds = computed({
  get: () => props.modelValue || [],
  set: (val) => emit('update:modelValue', val)
})

const isAllSelected = computed(() => {
  if (!props.data || props.data.length === 0) return false
  return props.data.every(item => selectedIds.value.includes(item.id))
})

const isIndeterminate = computed(() => {
  if (!props.data || props.data.length === 0) return false
  const selectedInPage = props.data.filter(item => selectedIds.value.includes(item.id))
  return selectedInPage.length > 0 && selectedInPage.length < props.data.length
})

const isSelected = (item: any) => {
  return selectedIds.value.includes(item.id)
}

const toggleSelect = (item: any) => {
  const newSelected = [...selectedIds.value]
  const index = newSelected.indexOf(item.id)
  if (index === -1) {
    newSelected.push(item.id)
  } else {
    newSelected.splice(index, 1)
  }
  emit('update:modelValue', newSelected)
}

const toggleSelectAll = () => {
  if (!props.data) return
  if (isAllSelected.value) {
    // Deselect all on current page
    const pageIds = props.data.map(item => item.id)
    const newSelected = selectedIds.value.filter(id => !pageIds.includes(id))
    emit('update:modelValue', newSelected)
  } else {
    // Select all on current page
    const pageIds = props.data.map(item => item.id)
    const uniqueSelected = new Set([...selectedIds.value, ...pageIds])
    emit('update:modelValue', Array.from(uniqueSelected))
  }
}
</script>