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
    <DataTable
      :columns="tableColumns"
      :data="users"
      :loading="isLoading"
      :actions="true"
      :empty-text="$t('admin.noUsersFound')"
    >
      <template #cell-is_active="{ item }">
        <span :class="['px-2 inline-flex text-xs leading-5 font-semibold rounded-full', item.is_active ? 'bg-green-100 text-green-800 dark:bg-green-800/30 dark:text-green-300' : 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300']">
          {{ item.is_active ? $t('admin.active') : $t('admin.inactive') }}
        </span>
      </template>
      <template #cell-roles="{ item }">
        <div class="flex flex-wrap gap-1">
          <span 
            v-for="role in item.roles" 
            :key="role.id" 
            class="px-2 py-0.5 text-xs font-medium rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300"
          >
            {{ role.name }}
          </span>
        </div>
      </template>
      <template #actions="{ item }">
        <a href="#" @click.prevent="openModal('edit', item)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</a>
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
              <div class="relative">
                <input type="password" v-model="editableUser.password" id="password" :type="showPassword ? 'text' : 'password'" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm pr-10" required>
                <button
                  type="button"
                  @click="showPassword = !showPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5 text-gray-700 dark:text-gray-300 focus:outline-none"
                >
                  <icon :name="showPassword ? 'heroicons:eye-slash' : 'heroicons:eye'" class="w-5 h-5" />
                </button>
              </div>
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
import { useSnackbar } from '~/composables/useSnackbar';
import { useUsers } from '~/composables/useUsers';
import DataTable from '~/components/common/DataTable.vue';
import { useI18n } from '#imports';
import type { User, Role, PaginatedResponse } from '~/types';

definePageMeta({
  permission: 'manage_users',
});

const { getUsers, createUser, updateUser, getRoles, isLoading } = useUsers();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

// State
const users = ref<User[]>([]);
const allRoles = ref<Role[]>([]);
const showModal = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const editableUser = ref<any>({});
const showPassword = ref(false);

// Pagination State
const currentPage = ref(1);
const totalUsers = ref(0);
const usersPerPage = 10;
const totalPages = computed(() => Math.ceil(totalUsers.value / usersPerPage));

// Table Columns
const tableColumns = computed(() => [
  { key: 'username', label: t('admin.username'), class: 'text-left' },
  { key: 'is_active', label: t('admin.activeStatus'), class: 'text-left' },
  { key: 'roles', label: t('admin.roles'), class: 'text-left' },
]);

// Computed
const modalTitle = computed(() => modalMode.value === 'create' ? t('admin.createUser') : t('admin.editUser'));

// Methods
const fetchUsersData = async () => {
  try {
    const skip = (currentPage.value - 1) * usersPerPage;
    const data = await getUsers({ skip, limit: usersPerPage });
    users.value = data.records;
    totalUsers.value = data.total;
  } catch (error) {
    // Snackbar message handled in composable
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchUsersData();
  }
};

const fetchRolesData = async () => {
  try {
    const data = await getRoles();
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

  try {
    if (isEdit) {
      await updateUser(editableUser.value.id, editableUser.value);
      // Snackbar message is now handled within useUsers composable
    } else {
      await createUser(editableUser.value);
      // Snackbar message is now handled within useUsers composable
    }
    await fetchUsersData();
    closeModal();
  } catch (error) {
    // Snackbar message is now handled within useUsers composable
  }
};

onMounted(() => {
  fetchUsersData();
  fetchRolesData();
});
</script>