<template>
  <div class="max-w-7xl mx-auto space-y-6 p-4">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.announcementsTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('admin.manageAnnouncementsDescription') }}</p>
    </div>

    <!-- Toolbar -->
    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <div class="w-1/3">
        <input 
          type="text" 
          v-model="searchQuery" 
          :placeholder="$t('admin.searchAnnouncementsPlaceholder')" 
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        >
      </div>
      <div>
        <button 
          @click="openModal('create')" 
          class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300"
        >
          {{ $t('admin.createAnnouncement') }}
        </button>
      </div>
    </div>

    <!-- Announcements Table -->
    <DataTable 
      :columns="tableColumns" 
      :data="announcements" 
      :loading="isLoading" 
      :actions="true"
      :empty-text="$t('admin.noAnnouncementsFound')"
    >
      <template #cell-tag="{ item }">
        <span :class="`px-2 py-1 rounded-full text-xs ${getTagClass(item.tag_type)}`">
          {{ item.tag }}
        </span>
      </template>
      
      <template #cell-is_active="{ item }">
        <span :class="`px-2 py-1 rounded-full text-xs ${item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' : 'bg-gray-100 text-gray-800 dark:bg-gray-900/30 dark:text-gray-400'}`">
          {{ item.is_active ? '啟用' : '停用' }}
        </span>
      </template>

      <template #cell-created_at="{ item }">
        {{ new Date(item.created_at).toLocaleDateString('zh-TW') }}
      </template>

      <template #actions="{ item }">
        <a href="#" @click.prevent="openModal('edit', item)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mr-4">編輯</a>
        <a href="#" @click.prevent="handleDelete(item.id)" class="text-red-600 dark:text-red-500 hover:text-red-900 dark:hover:text-red-400">刪除</a>
      </template>
    </DataTable>

    <!-- Pagination -->
    <div v-if="totalPages > 1" class="mt-6 flex justify-center">
      <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
        <button 
          @click="changePage(currentPage - 1)" 
          :disabled="currentPage === 1" 
          class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          {{ $t('pagination.previous') }}
        </button>
        <button 
          v-for="page in totalPages" 
          :key="page" 
          @click="changePage(page)" 
          :class="['relative inline-flex items-center px-4 py-2 border border-gray-300 dark:border-gray-600 text-sm font-medium', currentPage === page ? 'bg-primary-50 border-primary-500 text-primary-600 dark:bg-gray-900' : 'bg-white dark:bg-gray-800 text-gray-700 dark:text-gray-200 hover:bg-gray-50 dark:hover:bg-gray-700']"
        >
          {{ page }}
        </button>
        <button 
          @click="changePage(currentPage + 1)" 
          :disabled="currentPage === totalPages" 
          class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-800 text-sm font-medium text-gray-500 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-700 disabled:opacity-50"
        >
          {{ $t('pagination.next') }}
        </button>
      </nav>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-2xl mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ modalTitle }}</h3>
        <form @submit.prevent="handleSave">
          <div class="space-y-4">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div>
                <label for="title" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.title') }} ({{ $t('common.chinese') }})</label>
                <input 
                  type="text" 
                  v-model="editableAnnouncement.title" 
                  id="title" 
                  class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500" 
                  required
                >
              </div>
              <div>
                <label for="title_en" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.title') }} ({{ $t('common.englishOptional') }})</label>
                <input 
                  type="text" 
                  v-model="editableAnnouncement.title_en" 
                  id="title_en" 
                  class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500" 
                  :placeholder="$t('admin.englishTitle')"
                >
              </div>
            </div>
            
            <div class="grid grid-cols-2 gap-4">
              <div>
                <label for="tag" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.tag') }}</label>
                <input 
                  type="text" 
                  v-model="editableAnnouncement.tag" 
                  id="tag" 
                  class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500" 
                  :placeholder="$t('admin.tagPlaceholder')"
                  required
                >
              </div>
              
              <div>
                <label for="tag_type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.tagType') }}</label>
                <select 
                  v-model="editableAnnouncement.tag_type" 
                  id="tag_type" 
                  class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500"
                  required
                >
                  <option value="primary">{{ $t('admin.tagTypePrimary') }}</option>
                  <option value="success">{{ $t('admin.tagTypeSuccess') }}</option>
                  <option value="warning">{{ $t('admin.tagTypeWarning') }}</option>
                  <option value="danger">{{ $t('admin.tagTypeDanger') }}</option>
                  <option value="info">{{ $t('admin.tagTypeInfo') }}</option>
                </select>
              </div>
            </div>

            <div>
              <label for="content" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.content') }} ({{ $t('common.chinese') }})</label>
              <textarea 
                v-model="editableAnnouncement.content" 
                id="content" 
                rows="4" 
                class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500" 
                required
              ></textarea>
            </div>

            <div>
              <label for="content_en" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.content') }} ({{ $t('common.englishOptional') }})</label>
              <textarea 
                v-model="editableAnnouncement.content_en" 
                id="content_en" 
                rows="4" 
                class="mt-1 block w-full border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm px-3 py-2 focus:outline-none focus:ring-2 focus:ring-primary-500" 
                :placeholder="$t('admin.englishContent')"
              ></textarea>
            </div>

            <div v-if="modalMode === 'edit'" class="flex items-center">
              <input 
                type="checkbox" 
                v-model="editableAnnouncement.is_active" 
                id="is_active" 
                class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded"
              >
              <label for="is_active" class="ml-2 block text-sm text-gray-700 dark:text-gray-300">{{ $t('admin.enableAnnouncement') }}</label>
            </div>
          </div>

          <div class="flex justify-end space-x-4 mt-6">
            <button 
              type="button" 
              @click="closeModal" 
              class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 dark:text-gray-300 dark:bg-gray-600 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500"
            >
              {{ $t('common.cancel') }}
            </button>
            <button 
              type="submit" 
              class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700"
            >
              {{ $t('common.save') }}
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useSnackbar } from '~/composables/useSnackbar';
import { useAnnouncements } from '~/composables/useAnnouncements';
import DataTable from '~/components/common/DataTable.vue';
import { useI18n } from '#imports';

const { t } = useI18n();
const { getAnnouncements, createAnnouncement, updateAnnouncement, deleteAnnouncement, isLoading } = useAnnouncements();
const { showSnackbar } = useSnackbar();

// State
const announcements = ref([]);
const searchQuery = ref('');
const showModal = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const editableAnnouncement = ref<any>({});

// Table Columns
const tableColumns = computed(() => [
  { key: 'title', label: t('admin.title'), class: 'text-left', cellClass: 'font-medium text-gray-900 dark:text-white' },
  { key: 'tag', label: t('admin.tag'), class: 'text-left' },
  { key: 'is_active', label: t('admin.status'), class: 'text-left' },
  { key: 'created_at', label: t('admin.createdAt'), class: 'text-left', cellClass: 'text-gray-500 dark:text-gray-400' },
]);

// Pagination State
const currentPage = ref(1);
const totalAnnouncements = ref(0);
const announcementsPerPage = 10;
const totalPages = computed(() => Math.ceil(totalAnnouncements.value / announcementsPerPage));

// Computed
const modalTitle = computed(() => modalMode.value === 'create' ? t('admin.createAnnouncementTitle') : t('admin.editAnnouncementTitle'));

// Methods
const getTagClass = (tagType: string) => {
  const classes = {
    primary: 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400',
    success: 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400',
    warning: 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400',
    danger: 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400',
    info: 'bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400',
  };
  return classes[tagType] || classes.primary;
};

const fetchAnnouncements = async () => {
  // loading.value = true; // Managed by composable
  try {
    const skip = (currentPage.value - 1) * announcementsPerPage;
    const response = await getAnnouncements({ skip, limit: announcementsPerPage, search: searchQuery.value }); // Pass search query
    announcements.value = response.records;
    totalAnnouncements.value = response.total;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadAnnouncements'), type: 'error' });
    announcements.value = [];
    totalAnnouncements.value = 0;
  } finally {
    // loading.value = false; // Managed by composable
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchAnnouncements();
  }
};

const openModal = (mode: 'create' | 'edit', announcement: any = {}) => {
  modalMode.value = mode;
  if (mode === 'create') {
    editableAnnouncement.value = { title: '', title_en: '', content: '', content_en: '', tag: '', tag_type: 'primary' };
  } else {
    editableAnnouncement.value = { ...announcement };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const handleSave = async () => {
  const isEdit = modalMode.value === 'edit';
  
  try {
    if (isEdit) {
      await updateAnnouncement(editableAnnouncement.value.id, editableAnnouncement.value);
      // Snackbar message is now handled inside useAnnouncements composable
    } else {
      await createAnnouncement(editableAnnouncement.value);
      // Snackbar message is now handled inside useAnnouncements composable
    }
    
    await fetchAnnouncements();
    closeModal();
  } catch (error: any) {
    // Snackbar message is now handled inside useAnnouncements composable
  }
};

const handleDelete = async (id: string) => {
  if (!confirm(t('confirm.deleteAnnouncement'))) return; // Assuming a new i18n key

  try {
    await deleteAnnouncement(id);
    // Snackbar message is now handled inside useAnnouncements composable
    await fetchAnnouncements();
  } catch (error) {
    // Snackbar message is now handled inside useAnnouncements composable
  }
};

onMounted(() => {
  fetchAnnouncements();
});
</script>
