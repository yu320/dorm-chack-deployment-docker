<template>
  <div class="max-w-6xl mx-auto space-y-6 p-4">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.userManagement') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('admin.manageUsers') }}</p>
    </div>

    <!-- Toolbar -->
    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 flex justify-end items-center">
      <button @click="openModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
        {{ $t('admin.createUser') }}
      </button>
    </div>

    <!-- Users Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.username') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.activeStatus') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.roles') }}</th>
              <th scope="col" class="relative px-6 py-3"><span class="sr-only">{{ $t('admin.actions') }}</span></th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="user in users" :key="user.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ user.username }}</td>
              <td class="px-6 py-4 whitespace-nowrap">
                <span :class="['px-2 inline-flex text-xs leading-5 font-semibold rounded-full', user.is_active ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300']">
                  {{ user.is_active ? $t('admin.active') : $t('admin.inactive') }}
                </span>
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ user.roles.map(role => role.name).join(', ') }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="#" @click.prevent="openModal('edit', user)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</a>
              </td>
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
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-lg mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ modalTitle }}</h3>
        <form @submit.prevent="handleSave">
          <div class="space-y-4">
            <div>
              <label for="username" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.username') }}</label>
              <input type="text" v-model="editableUser.username" id="username" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div v-if="modalMode === 'create'">
              <label for="password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.password') }}</label>
              <input type="password" v-model="editableUser.password" id="password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
             <div v-if="modalMode === 'create'">
              <label for="studentIdNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.studentId') }}</label>
              <input type="text" v-model="editableUser.student_id_number" id="studentIdNumber" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div class="flex items-center">
              <input type="checkbox" v-model="editableUser.is_active" id="isActive" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
              <label for="isActive" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">{{ $t('admin.active') }}</label>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.roles') }}</label>
              <div class="mt-2 space-y-2">
                <div v-for="role in allRoles" :key="role.id" class="flex items-center">
                  <input type="checkbox" :id="`role-${role.id}`" :value="role.id" v-model="editableUser.roles" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
                  <label :for="`role-${role.id}`" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">{{ role.name }}</label>
                </div>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-4 mt-6">
            <button type="button" @click="closeModal" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 dark:text-gray-300 dark:bg-gray-600 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500">{{ $t('admin.cancel') }}</button>
            <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700">{{ $t('admin.save') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useI18n } from '#imports';

// Interfaces
interface Role {
  id: string;
  name: string;
}
interface User {
  id: string;
  username: string;
  is_active: boolean;
  roles: Role[];
}
interface PaginatedUserResponse {
  total: number;
  records: User[];
}

definePageMeta({
  permission: 'manage_users',
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

// State
const users = ref<User[]>([]);
const allRoles = ref<Role[]>([]);
const showModal = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const editableUser = ref<any>({});
const loading = ref(false);

// Pagination State
const currentPage = ref(1);
const totalUsers = ref(0);
const usersPerPage = 10;
const totalPages = computed(() => Math.ceil(totalUsers.value / usersPerPage));

// Computed
const modalTitle = computed(() => modalMode.value === 'create' ? t('admin.createUser') : t('admin.editUser'));

// Methods
const fetchUsers = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams({
      skip: ((currentPage.value - 1) * usersPerPage).toString(),
      limit: usersPerPage.toString(),
    });
    const data = await apiFetch(`/api/v1/users/?${params.toString()}`) as PaginatedUserResponse;
    users.value = data.records;
    totalUsers.value = data.total;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadUsers'), type: 'error' });
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchUsers();
  }
};

const fetchRoles = async () => {
  try {
    const data = await apiFetch('/api/v1/roles/');
    // Handle both paginated and direct array responses
    allRoles.value = (data.records || data) as Role[];
  } catch (error) {
    console.error("Failed to load roles", error);
  }
};

const openModal = (mode: 'create' | 'edit', user: any = {}) => {
  modalMode.value = mode;
  if (mode === 'create') {
    editableUser.value = { username: '', password: '', student_id_number: '', is_active: true, roles: [] };
  } else {
    // For editing, we only need role IDs
    editableUser.value = { ...user, roles: user.roles.map((r: Role) => r.id) };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const handleSave = async () => {
  const isEdit = modalMode.value === 'edit';
  const url = isEdit ? `/api/v1/users/${editableUser.value.id}` : '/api/v1/users/';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    await apiFetch(url, { method, body: editableUser.value });
    showSnackbar({ message: t(isEdit ? 'snackbar.userUpdated' : 'snackbar.userCreated'), type: 'success' });
    await fetchUsers();
    closeModal();
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToSaveUser'), type: 'error' });
  }
};

onMounted(() => {
  fetchUsers();
  fetchRoles();
});
</script>