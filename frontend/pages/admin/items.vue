<template>
  <div class="max-w-6xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.itemManagement') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2 text-center">{{ $t('admin.manageItems') }}</p>
    </div>

    <!-- Toolbar -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <div class="flex space-x-3">
        <button 
          @click="batchUpdateStatus(true)" 
          :disabled="selectedItems.length === 0 || loading"
          class="bg-green-600 hover:bg-green-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ $t('admin.batchActivate') }}
        </button>
        <button 
          @click="batchUpdateStatus(false)" 
          :disabled="selectedItems.length === 0 || loading"
          class="bg-red-600 hover:bg-red-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed"
        >
          {{ $t('admin.batchDeactivate') }}
        </button>
      </div>
      <button @click="openCreateModal" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
        {{ $t('admin.createItem') }}
      </button>
    </div>

    <!-- Items Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700">
            <tr>
              <th scope="col" class="px-2 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">
                <input type="checkbox" v-model="selectAll" @change="toggleSelectAll" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
              </th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.name') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.description') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.status') }}</th>
              <th scope="col" class="relative px-6 py-3">
                <span class="sr-only">{{ $t('admin.actions') }}</span>
              </th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="item in items" :key="item.id">
              <td class="px-2 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">
                <input type="checkbox" v-model="selectedItems" :value="item.id" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ item.name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ item.description }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span 
                  :class="[
                    'px-2 inline-flex text-xs leading-5 font-semibold rounded-full',
                    item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  {{ item.is_active ? $t('admin.active') : $t('admin.inactive') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="#" @click.prevent="openEditModal(item)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</a>
                <a href="#" @click.prevent="deleteItem(item.id)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">{{ $t('admin.delete') }}</a>
              </td>
            </tr>
            <tr v-if="items.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ $t('admin.noInspectionItemsFound') }}</td>
            </tr>
          </tbody>
        </table>
      </div>
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

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-8 bg-white dark:bg-gray-800 w-full max-w-md mx-auto rounded-lg shadow-lg">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ isEditMode ? $t('admin.editItem') : $t('admin.createItem') }}</h3>
        <form @submit.prevent="saveItem">
          <div class="mb-4">
            <label for="itemName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.name') }}</label>
            <input type="text" id="itemName" v-model="currentItem.name" class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500" required>
          </div>
          <div class="mb-4">
            <label for="itemDescription" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.description') }}</label>
            <textarea id="itemDescription" v-model="currentItem.description" rows="3" class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500"></textarea>
          </div>
          <div v-if="isEditMode" class="mb-4 flex items-center">
            <input type="checkbox" id="itemIsActive" v-model="currentItem.is_active" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
            <label for="itemIsActive" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">{{ $t('admin.active') }}</label>
          </div>
          <div class="flex justify-end space-x-3">
            <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 dark:text-gray-300 dark:bg-gray-600 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              {{ $t('admin.cancel') }}
            </button>
            <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              {{ $t('admin.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue';
import { useI18n } from '#imports';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';

interface InspectionItem {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
}

interface PaginatedItemsResponse {
  total: number;
  records: InspectionItem[];
}

definePageMeta({
  permission: 'manage_items',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const items = ref<InspectionItem[]>([]);
const showModal = ref(false);
const isEditMode = ref(false);
const loading = ref(true);
const currentItem = ref<Partial<InspectionItem>>({
  name: '',
  description: '',
  is_active: true,
});
const selectedItems = ref<string[]>([]);
const selectAll = ref(false);

// Pagination State
const currentPage = ref(1);
const totalItems = ref(0);
const itemsPerPage = 10;
const totalPages = computed(() => Math.ceil(totalItems.value / itemsPerPage));

const fetchItems = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      skip: ((currentPage.value - 1) * itemsPerPage).toString(),
      limit: itemsPerPage.toString(),
    });
    const response = await apiFetch(`/api/v1/items/?${params.toString()}`) as PaginatedItemsResponse;
    items.value = response.records;
    totalItems.value = response.total;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadItems'), type: 'error' });
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchItems();
  }
};

const openCreateModal = () => {
  isEditMode.value = false;
  currentItem.value = { name: '', description: '', is_active: true };
  showModal.value = true;
};

const openEditModal = (item: InspectionItem) => {
  isEditMode.value = true;
  currentItem.value = { ...item };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveItem = async () => {
  try {
    if (isEditMode.value && currentItem.value.id) {
      await apiFetch(`/api/v1/items/${currentItem.value.id}`, {
        method: 'PUT',
        body: currentItem.value,
      });
      showSnackbar({ message: t('snackbar.itemUpdated'), type: 'success' });
    } else {
      await apiFetch('/api/v1/items/', {
        method: 'POST',
        body: currentItem.value,
      });
      showSnackbar({ message: t('snackbar.itemCreated'), type: 'success' });
    }
    closeModal();
    await fetchItems();
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToSaveItem'), type: 'error' });
  }
};

const deleteItem = async (id: string) => {
  if (confirm(t('confirm.deleteItem'))) {
    try {
      await apiFetch(`/api/v1/items/${id}`, {
        method: 'DELETE',
      });
      showSnackbar({ message: t('snackbar.itemDeleted'), type: 'success' });
      await fetchItems();
    } catch (error) {
      showSnackbar({ message: t('snackbar.failedToDeleteItem'), type: 'error' });
    }
  }
};

const toggleSelectAll = () => {
  if (selectAll.value) {
    selectedItems.value = items.value.map(item => item.id);
  } else {
    selectedItems.value = [];
  }
};

watch(selectedItems, (newVal) => {
  if (items.value.length > 0) {
    selectAll.value = newVal.length === items.value.length;
  }
});

const batchUpdateStatus = async (is_active: boolean) => {
  if (selectedItems.value.length === 0) {
    showSnackbar({ message: t('snackbar.selectOneTable'), type: 'warning' });
    return;
  }
  
  if (confirm(t('confirm.batchUpdateItemStatus', { status: is_active ? t('admin.active') : t('admin.inactive') }))) {
    try {
      await apiFetch('/api/v1/items/batch-update-status', {
        method: 'PUT',
        body: { item_ids: selectedItems.value, is_active: is_active },
      });
      showSnackbar({ message: t('snackbar.batchUpdateItemStatusSuccess'), type: 'success' });
      selectedItems.value = [];
      selectAll.value = false;
      await fetchItems();
    } catch (error) {
      showSnackbar({ message: t('snackbar.batchUpdateItemStatusFailed'), type: 'error' });
    }
  }
};

onMounted(() => {
  fetchItems();
});
</script>