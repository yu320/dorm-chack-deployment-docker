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
        <button v-if="hasPermission('manage_patrol_locations')" @click="activeTab = 'patrol_locations'" :class="[activeTab === 'patrol_locations' ? 'border-primary-500 text-primary-600 dark:text-primary-400' : 'border-transparent text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300', 'whitespace-nowrap py-3 px-1 border-b-2 font-medium text-sm']">
          {{ $t('admin.patrolLocations') }}
        </button>
      </nav>

      <!-- Roles Tab -->
      <div v-if="activeTab === 'roles'">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold text-gray-700 dark:text-white">{{ $t('admin.roles') }}</h2>
          <button @click="openRoleModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md">
            {{ $t('admin.createRole') }}
          </button>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
            <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.name') }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.permissions') }}</th>
                <th class="relative px-6 py-3"><span class="sr-only">{{ $t('admin.actions') }}</span></th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="role in roles" :key="role.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ role.name }}</td>
                <td class="px-6 py-4 text-sm text-gray-500 dark:text-gray-400">
                  <span v-for="perm in role.permissions" :key="perm.id" class="mr-2 mb-2 inline-block bg-gray-200 dark:bg-gray-600 rounded-full px-3 py-1 text-xs font-semibold text-gray-700 dark:text-gray-200">
                    {{ $t('permissions.' + perm.name + '.title') }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="openRoleModal('edit', role)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</button>
                  <button @click="handleRoleDelete(role.id)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">{{ $t('admin.delete') }}</button>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
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
      <div v-if="activeTab === 'patrol_locations' && hasPermission('manage_patrol_locations')">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-2xl font-semibold text-gray-700 dark:text-white">{{ $t('admin.patrolLocations') }}</h2>
          <div class="flex items-center space-x-4">
            <select v-model="selectedBuildingId" class="block w-full max-w-xs border-gray-300 rounded-md shadow-sm">
              <option v-for="building in buildings" :key="building.id" :value="building.id">{{ building.name }}</option>
            </select>
            <button @click="openPatrolModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md">
              {{ $t('admin.createPatrolLocation') }}
            </button>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 rounded-lg shadow overflow-hidden border border-gray-200 dark:border-gray-700">
          <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
             <thead class="bg-gray-50 dark:bg-gray-700/50">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.name') }}</th>
                <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.household') }}</th>
                <th class="relative px-6 py-3"><span class="sr-only">{{ $t('admin.actions') }}</span></th>
              </tr>
            </thead>
            <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
              <tr v-for="location in patrolLocations" :key="location.id">
                <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ location.name }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ location.household }}</td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <button @click="openPatrolModal('edit', location)" class="text-primary-600 hover:text-primary-900 dark:text-primary-400 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</button>
                  <button @click="handlePatrolDelete(location.id)" class="text-red-600 hover:text-red-900 dark:text-red-400 dark:hover:text-red-300">{{ $t('admin.delete') }}</button>
                </td>
              </tr>
            </tbody>
          </table>
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
              <input type="text" v-model="editableRole.name" id="roleName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.permissions') }}</label>
              <div class="mt-2 grid grid-cols-2 md:grid-cols-3 gap-4 max-h-60 overflow-y-auto p-2 border rounded-md">
                <div v-for="permission in permissions" :key="permission.id" class="flex items-center">
                  <input type="checkbox" :id="`perm-${permission.id}`" :value="permission.id" v-model="editableRole.permissions" class="h-4 w-4 text-primary-600 focus:ring-primary-500 border-gray-300 rounded">
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
              <input type="text" v-model="editablePatrolLocation.name" id="patrolName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="patrolHousehold" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.householdOptional') }}</label>
              <input type="text" v-model="editablePatrolLocation.household" id="patrolHousehold" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
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
import { ref, onMounted, watch } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useI18n } from '#imports';

// Interfaces
interface Permission {
  id: string;
  name: string;
  description: string;
}
interface Role {
  id: string;
  name: string;
  permissions: Permission[];
}
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

// --- Methods for Roles ---
const fetchRoles = async () => {
  try {
    const response = await apiFetch('/api/v1/roles/');
    roles.value = response.records;
  } catch (e) { showSnackbar({ message: t('snackbar.failedToLoadRoles'), type: 'error' }); }
};

const fetchPermissions = async () => {
  try {
    const response = await apiFetch('/api/v1/permissions/');
    permissions.value = response.records;
  } catch (e) { showSnackbar({ message: t('snackbar.failedToLoadPermissions'), type: 'error' }); }
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
  const url = isEdit ? `/api/v1/roles/${editableRole.value.id}` : '/api/v1/roles/';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    await apiFetch(url, { method, body: editableRole.value });
    showSnackbar({ message: t(isEdit ? 'snackbar.roleUpdated' : 'snackbar.roleCreated'), type: 'success' });
    await fetchRoles();
    showRoleModal.value = false;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToSaveRole'), type: 'error' });
  }
};

const handleRoleDelete = async (id: string) => {
  if (!confirm(t('confirm.deleteRole'))) return;
  try {
    await apiFetch(`/api/v1/roles/${id}`, { method: 'DELETE' });
    showSnackbar({ message: t('snackbar.roleDeleted'), type: 'success' });
    await fetchRoles();
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToDeleteRole'), type: 'error' });
  }
};

// --- Methods for Patrol Locations ---
const fetchBuildings = async () => {
  try {
    buildings.value = await apiFetch('/api/v1/buildings/');
    if (buildings.value.length > 0 && !selectedBuildingId.value) {
      selectedBuildingId.value = buildings.value[0].id;
    }
  } catch (e) { showSnackbar(t('snackbar.failedToLoadBuildings'), 'error'); }
};

const fetchPatrolLocations = async () => {
  if (!selectedBuildingId.value) {
    patrolLocations.value = [];
    return;
  }
  try {
    const data = await apiFetch(`/api/v1/patrol-locations/?building_id=${selectedBuildingId.value}`);
    patrolLocations.value = data.records;
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
  const url = isEdit ? `/api/v1/patrol-locations/${editablePatrolLocation.value.id}` : '/api/v1/patrol-locations/';
  const method = isEdit ? 'PUT' : 'POST';

  try {
    await apiFetch(url, { method, body: editablePatrolLocation.value });
    showSnackbar({ message: t('snackbar.patrolLocationSaved'), type: 'success' });
    await fetchPatrolLocations();
    showPatrolModal.value = false;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToSavePatrolLocation'), type: 'error' });
  }
};

const handlePatrolDelete = async (id: string) => {
  if (!confirm(t('confirm.deletePatrolLocation'))) return;
  try {
    await apiFetch(`/api/v1/patrol-locations/${id}`, { method: 'DELETE' });
    showSnackbar({ message: t('snackbar.patrolLocationDeleted'), type: 'success' });
    await fetchPatrolLocations();
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToDeletePatrolLocation'), type: 'error' });
  }
};

// Watchers and Lifecycle
watch(selectedBuildingId, fetchPatrolLocations);

onMounted(() => {
  fetchRoles();
  fetchPermissions();
  fetchBuildings();
});
</script>