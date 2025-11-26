<template>
  <div class="max-w-7xl mx-auto space-y-6 p-4">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.roomManagement') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2 text-center">{{ $t('admin.manageRooms') }}</p>
    </div>

    <!-- Main Content Grid -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Buildings Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800 dark:text-white">{{ $t('admin.buildings') }}</h2>
          <button @click="openModal('building', 'create')" class="bg-primary-600 hover:bg-primary-700 text-white text-sm font-bold py-2 px-3 rounded-lg shadow-md transition duration-300">
            + {{ $t('admin.createBuilding') }}
          </button>
        </div>
        <ul class="space-y-2">
          <li v-for="building in buildingsTree" :key="building.id"
              @click="selectBuilding(building)"
              :class="['p-3 rounded-lg cursor-pointer transition-colors', selectedBuilding?.id === building.id ? 'bg-primary-100 dark:bg-primary-800/50 ring-2 ring-primary-500' : 'hover:bg-gray-100 dark:hover:bg-gray-700']">
            <div class="flex justify-between items-center">
              <span class="font-semibold text-gray-800 dark:text-gray-200">{{ building.name }}</span>
              <div class="flex items-center space-x-2">
                <button @click.stop="openModal('building', 'edit', building)" class="text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg></button>
                <button @click.stop="handleDelete('building', building.id)" class="text-gray-400 hover:text-red-600 dark:hover:text-red-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
              </div>
            </div>
          </li>
        </ul>
      </div>

      <!-- Rooms Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800 dark:text-white">{{ $t('admin.rooms') }}</h2>
          <button @click="openModal('room', 'create')" :disabled="!selectedBuilding" class="bg-primary-600 hover:bg-primary-700 text-white text-sm font-bold py-2 px-3 rounded-lg shadow-md transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed">
            + {{ $t('admin.createRoom') }}
          </button>
        </div>
        <ul v-if="selectedBuilding" class="space-y-2">
          <li v-for="room in selectedBuilding.rooms" :key="room.id"
              @click="selectRoom(room)"
              :class="['p-3 rounded-lg cursor-pointer transition-colors', selectedRoom?.id === room.id ? 'bg-primary-100 dark:bg-primary-800/50 ring-2 ring-primary-500' : 'hover:bg-gray-100 dark:hover:bg-gray-700']">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold text-gray-800 dark:text-gray-200">{{ room.room_number }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ room.room_type }}</p>
              </div>
              <div class="flex items-center space-x-2">
                <button @click.stop="openModal('room', 'edit', room)" class="text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg></button>
                <button @click.stop="handleDelete('room', room.id)" class="text-gray-400 hover:text-red-600 dark:hover:text-red-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 dark:text-gray-400 text-center mt-8">{{ $t('admin.selectBuildingPrompt') }}</p>
      </div>

      <!-- Beds Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md border border-gray-200 dark:border-gray-700">
        <div class="flex justify-between items-center mb-4">
          <h2 class="text-xl font-bold text-gray-800 dark:text-white">{{ $t('admin.beds') }}</h2>
          <button @click="openModal('bed', 'create')" :disabled="!selectedRoom" class="bg-primary-600 hover:bg-primary-700 text-white text-sm font-bold py-2 px-3 rounded-lg shadow-md transition duration-300 disabled:bg-gray-400 disabled:cursor-not-allowed">
            + {{ $t('admin.createBed') }}
          </button>
        </div>
        <ul v-if="selectedRoom" class="space-y-2">
          <li v-for="bed in selectedRoom.beds" :key="bed.id"
              class="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold text-gray-800 dark:text-gray-200">{{ bed.bed_number }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ $t(`admin.${bed.status.toLowerCase()}`) }}</p>
              </div>
              <div class="flex items-center space-x-2">
                <button @click.stop="openModal('bed', 'edit', bed)" class="text-gray-400 hover:text-primary-600 dark:hover:text-primary-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15.232 5.232l3.536 3.536m-2.036-5.036a2.5 2.5 0 113.536 3.536L6.5 21.036H3v-3.5L16.732 3.732z"></path></svg></button>
                <button @click.stop="handleDelete('bed', bed.id)" class="text-gray-400 hover:text-red-600 dark:hover:text-red-400"><svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"></path></svg></button>
              </div>
            </div>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 dark:text-gray-400 text-center mt-8">{{ $t('admin.selectRoomPrompt') }}</p>
      </div>
    </div>

    <!-- CRUD Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-lg mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ modalTitle }}</h3>
        <form @submit.prevent="handleSave">
          <!-- Building Fields -->
          <div v-if="modalTarget === 'building'" class="space-y-4">
            <div>
              <label for="buildingName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.buildingName') }}</label>
              <input type="text" v-model="editableItem.name" id="buildingName" class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-md shadow-sm py-2 px-3 bg-white dark:bg-gray-700 text-gray-900 dark:text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500" required>
            </div>
          </div>

          <!-- Room Fields -->
          <div v-if="modalTarget === 'room'" class="space-y-4">
            <div>
              <label for="roomNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.roomNumber') }}</label>
              <input type="text" v-model="editableItem.room_number" id="roomNumber" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="roomType" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.roomType') }}</label>
              <input type="text" v-model="editableItem.room_type" id="roomType" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
          </div>

          <!-- Bed Fields -->
          <div v-if="modalTarget === 'bed'" class="space-y-4">
            <div>
              <label for="bedNumber" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.bedNumber') }}</label>
              <input type="text" v-model="editableItem.bed_number" id="bedNumber" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
             <div>
              <label for="bedStatus" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('dashboard.status') }}</label>
              <select v-model="editableItem.status" id="bedStatus" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
                <option value="available">{{ $t('admin.available') }}</option>
                <option value="occupied">{{ $t('admin.occupied') }}</option>
                <option value="reserved">{{ $t('admin.reserved') }}</option>
              </select>
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

// Define interfaces for the data structure
interface Bed {
  id: number;
  bed_number: string;
  status: string;
}
interface Room {
  id: number;
  room_number: string;
  room_type: string;
  beds: Bed[];
}
interface Building {
  id: number;
  name: string;
  rooms: Room[];
}

definePageMeta({
  permission: 'manage_rooms',
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

// Reactive state
const buildingsTree = ref<Building[]>([]);
const selectedBuilding = ref<Building | null>(null);
const selectedRoom = ref<Room | null>(null);

const showModal = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const modalTarget = ref<'building' | 'room' | 'bed' | null>(null);
const editableItem = ref<any>({});

// Computed properties
const modalTitle = computed(() => {
  if (!modalTarget.value) return '';
  if (modalMode.value === 'create') {
    if (modalTarget.value === 'building') return t('admin.createBuildingTitle');
    if (modalTarget.value === 'room') return t('admin.createRoomTitle');
    if (modalTarget.value === 'bed') return t('admin.createBedTitle');
  } else {
    if (modalTarget.value === 'building') return t('admin.editBuildingTitle');
    if (modalTarget.value === 'room') return t('admin.editRoomTitle');
    if (modalTarget.value === 'bed') return t('admin.editBedTitle');
  }
  return '';
});

// Methods
const fetchTree = async () => {
  try {
    const data = await apiFetch('/api/v1/buildings/full-tree/');
    buildingsTree.value = data as Building[];
    // After fetching, re-select the items if they still exist
    if (selectedBuilding.value) {
      selectedBuilding.value = buildingsTree.value.find(b => b.id === selectedBuilding.value!.id) || null;
    }
    if (selectedBuilding.value && selectedRoom.value) {
      selectedRoom.value = selectedBuilding.value.rooms.find(r => r.id === selectedRoom.value!.id) || null;
    } else {
      selectedRoom.value = null;
    }
  } catch (error) {

    showSnackbar(t('snackbar.failedToLoadData'), 'error');
  }
};

const selectBuilding = (building: Building) => {
  selectedBuilding.value = building;
  selectedRoom.value = null; // Reset room selection
};

const selectRoom = (room: Room) => {
  selectedRoom.value = room;
};

const openModal = (target: 'building' | 'room' | 'bed', mode: 'create' | 'edit', item: any = {}) => {
    modalTarget.value = target;
  modalMode.value = mode;
  if (mode === 'create') {
    editableItem.value = {};
  } else {
    editableItem.value = { ...item };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
  modalTarget.value = null;
  editableItem.value = {};
};

const handleSave = async () => {
  const target = modalTarget.value;
  const mode = modalMode.value;
  let url = `/api/v1/${target}s/`;
  let method: 'POST' | 'PUT' = 'POST';

  const body = { ...editableItem.value };

  if (mode === 'edit') {
    url = `/api/v1/${target}s/${body.id}`;
    method = 'PUT';
  } else {
    if (target === 'room') body.building_id = selectedBuilding.value?.id;
    if (target === 'bed') body.room_id = selectedRoom.value?.id;
  }

  try {
    await apiFetch(url, { method, body });
    showSnackbar(t('snackbar.itemSaved', { item: target }), 'success');
    await fetchTree();
    closeModal();
  } catch (error) {

    showSnackbar(t('snackbar.failedToSaveItem', { item: target }), 'error');
  }
};

const handleDelete = async (target: 'building' | 'room' | 'bed', id: number) => {
  if (!confirm(t('confirm.deleteItem', { item: target }))) return;

  try {
    await apiFetch(`/api/v1/${target}s/${id}`, { method: 'DELETE' });
    showSnackbar(t('snackbar.itemDeleted', { item: target }), 'success');
    await fetchTree();
  } catch (error) {

    showSnackbar(t('snackbar.failedToDeleteItem', { item: target }), 'error');
  }
};

onMounted(fetchTree);
</script>
