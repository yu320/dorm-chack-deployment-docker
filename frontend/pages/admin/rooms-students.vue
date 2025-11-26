<template>
  <div class="max-w-7xl mx-auto space-y-6 p-4">
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.roomsStudents.title') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2 text-center">{{ $t('admin.roomsStudents.description') }}</p>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <!-- Buildings Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.roomsStudents.buildingsTitle') }}</h2>
        <ul class="space-y-2">
          <li v-for="building in buildingsTree" :key="building.id"
              @click="selectBuilding(building)"
              :class="['p-3 rounded-lg cursor-pointer', selectedBuilding?.id === building.id ? 'bg-primary-100 dark:bg-primary-800/50' : 'hover:bg-gray-100 dark:hover:bg-gray-700']">
            <span class="font-semibold">{{ building.name }}</span>
          </li>
        </ul>
      </div>

      <!-- Rooms Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.roomsStudents.roomsTitle') }}</h2>
        <ul v-if="selectedBuilding" class="space-y-2">
          <li v-for="room in selectedBuilding.rooms" :key="room.id"
              @click="selectRoom(room)"
              :class="['p-3 rounded-lg cursor-pointer', selectedRoom?.id === room.id ? 'bg-primary-100 dark:bg-primary-800/50' : 'hover:bg-gray-100 dark:hover:bg-gray-700']">
            <p class="font-semibold">{{ room.room_number }}</p>
            <p class="text-xs text-gray-500">{{ room.room_type }}</p>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 text-center mt-8">{{ $t('admin.roomsStudents.selectBuildingPrompt') }}</p>
      </div>

      <!-- Students/Beds Column -->
      <div class="bg-white dark:bg-gray-800 p-5 rounded-lg shadow-md">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.roomsStudents.bedsTitle') }}</h2>
        <ul v-if="selectedRoom" class="space-y-2">
          <li v-for="bed in selectedRoom.beds" :key="bed.id" class="p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700">
            <div class="flex justify-between items-center">
              <div>
                <p class="font-semibold">{{ bed.bed_number }}</p>
                <p v-if="getStudentByBedId(bed.id)" class="text-sm text-gray-600 dark:text-gray-300">{{ getStudentByBedId(bed.id)?.full_name }}</p>
                <p v-else class="text-sm text-green-600 dark:text-green-400">{{ $t('admin.roomsStudents.available') }}</p>
              </div>
              <button v-if="!getStudentByBedId(bed.id)" @click="openAssignModal(bed)" class="text-sm bg-primary-500 hover:bg-primary-600 text-white py-1 px-3 rounded">{{ $t('admin.roomsStudents.assign') }}</button>
              <button v-else @click="unassignStudent(getStudentByBedId(bed.id)!)" class="text-sm bg-red-500 hover:bg-red-600 text-white py-1 px-3 rounded">{{ $t('admin.roomsStudents.unassign') }}</button>
            </div>
          </li>
        </ul>
        <p v-else class="text-sm text-gray-500 text-center mt-8">{{ $t('admin.roomsStudents.selectRoomPrompt') }}</p>
      </div>
    </div>

    <!-- Assign Student Modal -->
    <div v-if="showAssignModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 z-50 flex justify-center items-center">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-xl w-full max-w-md">
        <h3 class="text-xl font-bold mb-4">{{ $t('admin.roomsStudents.assignModalTitle', { bedNumber: selectedBed?.bed_number }) }}</h3>
        <input type="text" v-model="studentSearchQuery" :placeholder="$t('admin.roomsStudents.searchPlaceholder')" class="w-full px-3 py-2 border rounded-md mb-4">
        <ul class="max-h-60 overflow-y-auto">
          <li v-for="student in unassignedStudents" :key="student.id" @click="assignStudent(student)" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer rounded">
            {{ student.full_name }} ({{ student.student_id_number }})
          </li>
        </ul>
        <div class="flex justify-end mt-4">
          <button @click="closeAssignModal" class="px-4 py-2 text-gray-700 bg-gray-200 rounded-md">{{ $t('admin.cancel') }}</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';

definePageMeta({
  permission: 'manage_students',
});

// Interfaces
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
interface Student {
  id: string;
  full_name: string;
  student_id_number: string;
  bed_id: number | null;
}

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

const buildingsTree = ref<Building[]>([]);
const allStudents = ref<Student[]>([]);
const selectedBuilding = ref<Building | null>(null);
const selectedRoom = ref<Room | null>(null);
const selectedBed = ref<Bed | null>(null);
const showAssignModal = ref(false);
const studentSearchQuery = ref('');

const fetchTree = async () => {
  try {
    buildingsTree.value = await apiFetch('/api/v1/buildings/full-tree/');
  } catch (error) {
    showSnackbar(t('snackbar.failedToLoadBuildings'), 'error');
  }
};

const fetchStudents = async () => {
  try {
    // This page needs all students for its logic, so we fetch with a very high limit.
    // A better long-term solution might be a dedicated endpoint or more server-side filtering.
    const response = await apiFetch('/api/v1/students/?limit=10000') as PaginatedStudentResponse;
    allStudents.value = response.records;
  } catch (error) {
    showSnackbar(t('snackbar.failedToLoadStudents'), 'error');
  }
};

onMounted(() => {
  fetchTree();
  fetchStudents();
});

const selectBuilding = (building: Building) => {
  selectedBuilding.value = building;
  selectedRoom.value = null;
};

const selectRoom = (room: Room) => {
  selectedRoom.value = room;
};

const getStudentByBedId = (bedId: number) => {
  return allStudents.value.find(s => s.bed_id === bedId);
};

const unassignedStudents = computed(() => {
  const query = studentSearchQuery.value.toLowerCase();
  return allStudents.value.filter(s => !s.bed_id && s.full_name.toLowerCase().includes(query));
});

const openAssignModal = (bed: Bed) => {
  selectedBed.value = bed;
  showAssignModal.value = true;
};

const closeAssignModal = () => {
  showAssignModal.value = false;
  selectedBed.value = null;
  studentSearchQuery.value = '';
};

const assignStudent = async (student: Student) => {
  if (!selectedBed.value) return;
  try {
    await apiFetch(`/api/v1/students/${student.id}/assign-bed`, {
      method: 'PUT',
      body: { bed_id: selectedBed.value.id },
    });
    showSnackbar(t('admin.roomsStudents.assignSuccess'), 'success');
    await fetchStudents(); // Refresh student list
    closeAssignModal();
  } catch (error) {
    showSnackbar(t('admin.roomsStudents.assignFailed'), 'error');
  }
};

const unassignStudent = async (student: Student) => {
  if (!confirm(t('admin.roomsStudents.unassignConfirm', { studentName: student.full_name }))) return;
  try {
    await apiFetch(`/api/v1/students/${student.id}/assign-bed`, {
      method: 'PUT',
      body: { bed_id: null },
    });
    showSnackbar(t('admin.roomsStudents.unassignSuccess'), 'success');
    await fetchStudents(); // Refresh student list
  } catch (error) {
    showSnackbar(t('admin.roomsStudents.unassignFailed'), 'error');
  }
};
</script>