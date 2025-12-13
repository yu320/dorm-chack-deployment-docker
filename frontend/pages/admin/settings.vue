<template>
  <div class="max-w-6xl mx-auto space-y-6 p-4">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.settings') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2 text-center">{{ $t('admin.manageSettings') }}</p>
    </div>

    <!-- Tabs -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
      <nav class="-mb-px flex space-x-8 border-b border-gray-200 dark:border-gray-700 mb-6" aria-label="Tabs">
        <button @click="activeTab = 'roles'" :class="[activeTab === 'roles' ? 'border-primary-500 text-primary-600 dark:text-primary-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300', 'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm']">
          {{ $t('admin.roles') }}
        </button>
        <button @click="activeTab = 'permissions'" :class="[activeTab === 'permissions' ? 'border-primary-500 text-primary-600 dark:text-primary-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300', 'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm']">
          {{ $t('admin.permissions') }}
        </button>
        <button v-if="hasPermission('patrol_locations:view')" @click="activeTab = 'patrol_locations'" :class="[activeTab === 'patrol_locations' ? 'border-primary-500 text-primary-600 dark:text-primary-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300', 'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm']">
          {{ $t('admin.patrolLocations') }}
        </button>
        <button v-if="hasPermission('manage_system')" @click="activeTab = 'email'" :class="[activeTab === 'email' ? 'border-primary-500 text-primary-600 dark:text-primary-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300', 'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm']">
          {{ $t('admin.emailSettings') }}
        </button>
      </nav>

      <!-- Roles Tab -->
      <div v-if="activeTab === 'roles'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold text-gray-700 dark:text-white">{{ $t('admin.roles') }}</h2>
          <button v-if="hasPermission('roles:manage')" @click="openRoleModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md">
            {{ $t('admin.createRole') }}
          </button>
        </div>
        <DataTable
          :columns="roleTableColumns"
          :data="roles"
          :loading="isLoading"
          :actions="true"
          :empty-text="$t('admin.noRolesFound')"
        >
          <template #cell-permissions="{ item }">
            <span v-for="perm in item.permissions" :key="perm.id" class="mr-2 mb-2 inline-block bg-gray-200 dark:bg-gray-600 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 dark:text-gray-200">
              {{ $t('permissions.' + perm.name + '.title') }}
            </span>
          </template>
          <template #actions="{ item }">
            <button v-if="hasPermission('roles:manage')" @click.prevent="openRoleModal('edit', item)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</button>
            <button v-if="hasPermission('roles:manage')" @click.prevent="handleRoleDelete(item.id)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">{{ $t('admin.delete') }}</button>
          </template>
        </DataTable>
      </div>

      <!-- Permissions Tab -->
      <div v-if="activeTab === 'permissions'">
        <h2 class="text-2xl font-semibold text-gray-700 dark:text-white mb-4">{{ $t('admin.permissions') }}</h2>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
          <ul class="divide-y divide-gray-200 dark:divide-gray-700">
            <li v-for="permission in permissions" :key="permission.id" class="px-6 py-4">
              <p class="text-sm font-medium text-gray-900 dark:text-white">{{ $t('permissions.' + permission.name + '.title') }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('permissions.' + permission.name + '.description') }}</p>
            </li>
          </ul>
        </div>
      </div>

      <!-- Patrol Locations Tab -->
      <div v-if="activeTab === 'patrol_locations' && hasPermission('patrol_locations:view')">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold text-gray-700 dark:text-white">{{ $t('admin.patrolLocations') }}</h2>
          <div class="flex items-center space-x-4">
            <select v-model="selectedBuildingId" class="block w-full max-w-xs border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              <option v-for="building in buildings" :key="building.id" :value="building.id">{{ building.name }}</option>
            </select>
            <button v-if="hasPermission('patrol_locations:manage')" @click="openPatrolModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md">
              {{ $t('admin.createPatrolLocation') }}
            </button>
          </div>
        </div>
        <DataTable
          :columns="patrolLocationTableColumns"
          :data="patrolLocations"
          :loading="isLoading"
          :actions="true"
          :empty-text="$t('admin.noPatrolLocationsFound')"
        >
          <template #actions="{ item }">
            <button v-if="hasPermission('patrol_locations:manage')" @click.prevent="openPatrolModal('edit', item)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</button>
            <button v-if="hasPermission('patrol_locations:manage')" @click.prevent="handlePatrolDelete(item.id)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">{{ $t('admin.delete') }}</button>
          </template>
        </DataTable>
      </div>

      <!-- Email Settings Tab -->
      <div v-if="activeTab === 'email' && hasPermission('manage_system')">
        <h2 class="text-2xl font-semibold text-gray-700 dark:text-white mb-4">{{ $t('admin.emailSettings') }}</h2>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
          <form @submit.prevent="saveEmailSettings" class="space-y-6 max-w-2xl">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP Server</label>
                <input type="text" v-model="emailSettings.mail_server" class="w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">SMTP Port</label>
                <input type="number" v-model="emailSettings.mail_port" class="w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Username</label>
                <input type="text" v-model="emailSettings.mail_username" class="w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              </div>
              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Password</label>
                <input type="password" v-model="emailSettings.mail_password" class="w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              </div>
              <div class="md:col-span-2">
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Sender Email (From)</label>
                <input type="text" v-model="emailSettings.mail_from" class="w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
              </div>
              <div class="flex items-center">
                <input type="checkbox" v-model="emailSettings.mail_tls" id="mail_tls" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700">
                <label for="mail_tls" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">Use TLS</label>
              </div>
              <div class="flex items-center">
                <input type="checkbox" v-model="emailSettings.mail_ssl" id="mail_ssl" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700">
                <label for="mail_ssl" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">Use SSL</label>
              </div>
            </div>
            <div class="flex justify-end pt-4">
               <button type="submit" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-6 rounded-lg shadow-md transition duration-150 ease-in-out">
                 {{ $t('admin.saveSettings') }}
               </button>
            </div>
          </form>
        </div>
      </div>
    </div>

    <!-- Role Modal -->
    <div v-if="showRoleModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-2xl mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ roleModalMode === 'create' ? t('admin.createRole') : t('admin.editRole') }}</h3>
        <form @submit.prevent="handleRoleSave">
          <div class="space-y-4">
            <div>
              <label for="roleName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.name') }}</label>
              <input type="text" v-model="editableRole.name" id="roleName" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" required>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.permissions') }}</label>
              <div class="mt-2 grid grid-cols-2 md:grid-cols-3 gap-4 max-h-60 overflow-y-auto p-2 border rounded-md">
                <div v-for="permission in permissions" :key="permission.id" class="flex items-center">
                  <input type="checkbox" :id="`perm-${permission.id}`" :value="permission.id" v-model="editableRole.permissions" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 dark:border-gray-600 rounded bg-white dark:bg-gray-700">
                  <label :for="`perm-${permission.id}`" class="ml-2 block text-sm text-gray-900 dark:text-gray-300">{{ $t('permissions.' + permission.name + '.title') }}</label>
                </div>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-4 mt-6">
            <button type="button" @click="showRoleModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md">{{ $t('admin.cancel') }}</button>
            <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md">{{ $t('admin.save') }}</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Patrol Location Modal -->
    <div v-if="showPatrolModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-lg mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ patrolModalMode === 'create' ? t('admin.createPatrolLocation') : t('admin.editPatrolLocation') }}</h3>
        <form @submit.prevent="handlePatrolSave">
          <div class="space-y-4">
            <div>
              <label for="patrolName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.name') }}</label>
              <input type="text" v-model="editablePatrolLocation.name" id="patrolName" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white" required>
            </div>
            <div>
              <label for="patrolHousehold" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.householdOptional') }}</label>
              <input type="text" v-model="editablePatrolLocation.household" id="patrolHousehold" class="mt-1 block w-full border-gray-300 dark:border-gray-600 rounded-md shadow-sm bg-white dark:bg-gray-700 text-gray-900 dark:text-white">
            </div>
          </div>
          <div class="flex justify-end space-x-4 mt-6">
            <button type="button" @click="showPatrolModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md">{{ $t('admin.cancel') }}</button>
            <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md">{{ $t('admin.save') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch, computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useUsers } from '~/composables/useUsers'; // Import useUsers
import { useI18n } from '#imports';
import type { Role, Permission, PaginatedResponse } from '~/types'; // Import types
import DataTable from '~/components/common/DataTable.vue'; // Explicitly import DataTable

// Interfaces
interface PatrolLocation {
  id: string;
  name: string;
  building_id: number;
  household: string | null;
}
interface Building {
  id: number;
  name: string;
}

definePageMeta({
  permission: 'manage_roles',
});

const { apiFetch, hasPermission } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();
const { getRoles, createRole, updateRole, deleteRole, getPermissions, isLoading } = useUsers(); // Destructure useUsers

// General State
const activeTab = ref('roles');

// State for Roles
const roles = ref<Role[]>([]);
const permissions = ref<Permission[]>([]);
const showRoleModal = ref(false);
const roleModalMode = ref<'create' | 'edit'>('create');
const editableRole = ref<any>({});

// State for Patrol Locations
const patrolLocations = ref<PatrolLocation[]>([]);
const buildings = ref<Building[]>([]);
const selectedBuildingId = ref<number | null>(null);
const showPatrolModal = ref(false);
const patrolModalMode = ref<'create' | 'edit'>('create');
const editablePatrolLocation = ref<any>({});

const { 
  create: createPatrol, 
  update: updatePatrol, 
  remove: removePatrol, 
  getAll: getPatrols 
} = useGenericCrud<PatrolLocation>('/api/v1/patrol-locations/');

// State for Email Settings
const emailSettings = ref({
  mail_server: '',
  mail_port: 587,
  mail_username: '',
  mail_password: '',
  mail_from: '',
  mail_tls: true,
  mail_ssl: false
});

// Computed Columns
const roleTableColumns = computed(() => [
  { key: 'name', label: t('admin.name') },
  { key: 'permissions', label: t('admin.permissions') },
]);

const patrolLocationTableColumns = computed(() => [
  { key: 'name', label: t('admin.name') },
  { key: 'household', label: t('admin.household') },
]);

// --- Methods for Email Settings ---
const fetchEmailSettings = async () => {
  if (!hasPermission('manage_system')) return;
  try {
    const settingsList = await apiFetch('/api/v1/system-settings/');
    if (Array.isArray(settingsList)) {
      settingsList.forEach((setting: any) => {
        const key = setting.key;
        if (key in emailSettings.value) {
           if (key === 'mail_tls' || key === 'mail_ssl') {
                (emailSettings.value as any)[key] = setting.value === 'true';
            } else {
                (emailSettings.value as any)[key] = setting.value;
            }
        }
      });
    }
  } catch (error) {
    console.error('Error fetching email settings:', error);
    showSnackbar({ message: t('snackbar.failedToLoadData'), type: 'error' });
  }
};

const saveEmailSettings = async () => {
  try {
    const promises = Object.entries(emailSettings.value).map(([key, value]) => {
      return apiFetch(`/api/v1/system-settings/${key}`, {
        method: 'PUT',
        body: { value: String(value) }
      });
    });
    await Promise.all(promises);
    showSnackbar({ message: t('admin.saveSuccess'), type: 'success' });
  } catch (error) {
    showSnackbar({ message: t('admin.saveFailed'), type: 'error' });
  }
};


// --- Methods for Roles ---
const fetchRoles = async () => {
  try {
    const response = await getRoles() as PaginatedResponse<Role>;
    console.log('fetchRoles response:', response); // Debug log
    if (response && response.records) {
      roles.value = response.records;
      console.log('Roles set to:', roles.value); // Debug log
    } else {
      console.warn('getRoles did not return expected data structure:', response);
      roles.value = [];
    }
  } catch (e: any) { 
    console.error('Error fetching roles in settings.vue:', e); // Debug log
    showSnackbar({ message: e.message || t('snackbar.failedToLoadRoles'), type: 'error' });
    roles.value = [];
  }
};

const fetchPermissions = async () => {
  try {
    const response = await getPermissions() as PaginatedResponse<Permission>;
    permissions.value = response.records;
  } catch (e) { /* Snackbar message handled in composable */ }
};

const openRoleModal = (mode: 'create' | 'edit', role: any = {}) => {
  roleModalMode.value = mode;
  if (mode === 'create') {
    editableRole.value = { name: '', permissions: [] };
  } else {
    editableRole.value = { ...role, permissions: role.permissions.map((p: Permission) => p.id) };
  }

  showRoleModal.value = true;
};

const handleRoleSave = async () => {
  const isEdit = roleModalMode.value === 'edit';
  try {
    if (isEdit) {
        await updateRole(editableRole.value.id, editableRole.value);
        // Snackbar message handled in composable
    } else {
        await createRole(editableRole.value);
        // Snackbar message handled in composable
    }
    await fetchRoles();
    showRoleModal.value = false;
  } catch (error) {
    // Snackbar message handled in composable
  }
};

const handleRoleDelete = async (id: string) => {
  if (!confirm(t('confirm.deleteRole'))) return;
  try {
    await deleteRole(id);
    // Snackbar message handled in composable
    await fetchRoles();
  } catch (error) {
    // Snackbar message handled in composable
  }
};

// --- Methods for Patrol Locations ---
const fetchBuildings = async () => {
  try {
    const data = await apiFetch('/api/v1/buildings') as Building[]; // Removed trailing slash
    buildings.value = data;
    if (buildings.value.length > 0 && !selectedBuildingId.value) {
      selectedBuildingId.value = buildings.value[0].id;
    }
  } catch (e) { showSnackbar({ message: t('snackbar.failedToLoadBuildings'), type: 'error' }); }
};

const fetchPatrolLocations = async () => {
  if (!selectedBuildingId.value) {
    patrolLocations.value = [];
    return;
  }
  try {
    const data = await getPatrols({ building_id: selectedBuildingId.value }) as any; // useGenericCrud returns array, but check if it's wrapped
    // The API endpoint /api/v1/patrol-locations might return PaginatedResponse or List.
    // Checking crud_patrol_location.py or endpoint would be good, but let's assume it matches getGenericCrud T[].
    // If it returns { records: ... }, we need to handle it.
    // Let's check backend later if this fails. Assuming List for now based on useGenericCrud typing.
    // Actually, looking at other usage, it seems to return PaginatedResponse usually.
    if (data.records) {
        patrolLocations.value = data.records;
    } else if (Array.isArray(data)) {
        patrolLocations.value = data;
    } else {
        patrolLocations.value = [];
    }
  } catch (e) { 
    patrolLocations.value = [];
    showSnackbar({ message: t('snackbar.failedToLoadPatrolLocations'), type: 'error' }); 
  }
};

const openPatrolModal = (mode: 'create' | 'edit', location: any = {}) => {
  patrolModalMode.value = mode;
  if (mode === 'create') {
    editablePatrolLocation.value = { name: '', household: '', building_id: selectedBuildingId.value };
  } else {
    editablePatrolLocation.value = { ...location };
  }
  showPatrolModal.value = true;
};

const handlePatrolSave = async () => {
  const isEdit = patrolModalMode.value === 'edit';

  try {
    if (isEdit) {
      await updatePatrol(editablePatrolLocation.value.id, editablePatrolLocation.value);
    } else {
      await createPatrol(editablePatrolLocation.value);
    }
    // Snackbar message is now handled in composable
    await fetchPatrolLocations();
    showPatrolModal.value = false;
  } catch (error) {
    // Snackbar message is now handled in composable
  }
};

const handlePatrolDelete = async (id: string) => {
  if (!confirm(t('confirm.deletePatrolLocation'))) return;
  try {
    await removePatrol(id);
    // Snackbar message is now handled in composable
    await fetchPatrolLocations();
  } catch (error) {
    // Snackbar message is now handled in composable
  }
};

// Watchers and Lifecycle
watch(selectedBuildingId, fetchPatrolLocations);

onMounted(() => {
  fetchRoles();
  fetchPermissions();
  fetchBuildings();
  fetchEmailSettings();
});
</script>