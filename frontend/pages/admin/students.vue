<template>
  <div class="max-w-7xl mx-auto space-y-6 p-4">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('admin.studentManagement') }}</h1>
      <p class="text-gray-600 dark:text-gray-300 mt-2 text-center">{{ $t('admin.manageStudentProfiles') }}</p>
    </div>

    <!-- Toolbar -->
    <div class="bg-white dark:bg-gray-800 p-4 rounded-lg shadow-md border border-gray-200 dark:border-gray-700 flex justify-between items-center">
      <div class="w-1/3">
        <input
          type="text"
          v-model="searchQuery"
          :placeholder="$t('admin.searchStudents')"
          class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500"
        />
      </div>
      <div>
        <button @click="openModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
          {{ $t('admin.createStudent') }}
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <DataTable
      :columns="tableColumns"
      :data="students"
      :loading="loading"
      :actions="true"
      :empty-text="$t('admin.noStudentsFound')"
      :current-page="currentPage"
      :total-pages="totalPages"
      @page-change="changePage"
    >
      <template #cell-full_name="{ item }">
        <span class="font-medium text-gray-900 dark:text-white">{{ item.full_name }}</span>
      </template>
      <template #cell-student_id_number="{ item }">
        <span class="text-gray-500 dark:text-gray-400">{{ item.student_id_number }}</span>
      </template>
      <template #cell-class_name="{ item }">
        <span class="text-gray-500 dark:text-gray-400">{{ item.class_name }}</span>
      </template>
      <template #cell-room_info="{ item }">
        <span class="text-gray-500 dark:text-gray-400">
          {{ item.bed ? `${item.bed.room.room_number} / ${item.bed.bed_number}` : 'N/A' }}
        </span>
      </template>
      <template #actions="{ item }">
        <a href="#" @click.prevent="openModal('edit', item)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</a>
        <a href="#" @click.prevent="handleDelete(item.id)" class="text-red-600 dark:text-red-500 hover:text-red-900 dark:hover:text-red-400">{{ $t('admin.delete') }}</a>
      </template>
    </DataTable>

    <!-- Create/Edit Modal -->
    <div v-if="showModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-lg mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ modalTitle }}</h3>
        <form @submit.prevent="handleSave">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.fullName') }}</label>
              <input type="text" v-model="editableStudent.full_name" id="fullName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required />
            </div>
            <div>
              <label for="studentId" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.studentId') }}</label>
              <input type="text" v-model="editableStudent.student_id_number" id="studentId" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required />
            </div>
            <div>
              <label for="className" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.class') }}</label>
              <input type="text" v-model="editableStudent.class_name" id="className" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" />
            </div>
            <div>
              <label for="bedId" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.beds') }}</label>
              <NestedSelect
                v-model="editableStudent.bed_id"
                :options="buildingsTree"
                :loading="treeLoading"
                :original-bed-id="originalBedId"
                :placeholder="$t('admin.selectBed')"
              ></NestedSelect>
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
import { ref, onMounted, computed, watch } from 'vue';
import { debounce } from 'lodash-es';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useStudents } from '~/composables/useStudents'; // Import useStudents
import { useBuildings } from '~/composables/useBuildings'; // Import useBuildings
import NestedSelect from '~/components/common/NestedSelect.vue';
import DataTable from '~/components/common/DataTable.vue'; // Explicitly import DataTable
import { useI18n } from '#imports';
import type { Student, Building } from '~/types'; // Import Student and Building from types

// Interfaces (These are now imported from ~/types)
// interface Student { /* ... */ }
// interface Building { /* ... */ }

interface PaginatedStudentResponse {
  total: number;
  records: Student[];
}

definePageMeta({
  permission: 'manage_students',
});

const { apiFetch } = useAuth(); // Keep apiFetch for now for other calls if any
const { showSnackbar } = useSnackbar();
const { t } = useI18n();
const { getStudents, createStudent, updateStudent, assignBed, deleteStudent, isLoading: isStudentsLoading } = useStudents();
const { getBuildingsFullTree, isLoading: isBuildingsLoading } = useBuildings();

// State
const students = ref<Student[]>([]);
const buildingsTree = ref<Building[]>([]);
const treeLoading = computed(() => isBuildingsLoading.value); // Use composable loading
const loading = computed(() => isStudentsLoading.value); // Use composable loading
const searchQuery = ref('');
const showModal = ref(false);
const modalMode = ref<'create' | 'edit'>('create');
const editableStudent = ref<any>({});
const originalBedId = ref<number | null>(null);

// Pagination State
const currentPage = ref(1);
const totalStudents = ref(0);
const studentsPerPage = 10;
const totalPages = computed(() => Math.ceil(totalStudents.value / studentsPerPage));

// Computed
const modalTitle = computed(() => modalMode.value === 'create' ? t('admin.createStudent') : t('admin.editStudent'));

const tableColumns = computed(() => [
  { key: 'full_name', label: t('admin.fullName') },
  { key: 'student_id_number', label: t('admin.studentId') },
  { key: 'class_name', label: t('admin.class') },
  { key: 'room_info', label: t('admin.roomInfo') },
]);

// Methods
const fetchStudents = async () => {
  try {
    const params = new URLSearchParams();
    if (searchQuery.value) {
      params.append('full_name', searchQuery.value);
    }
    params.append('skip', ((currentPage.value - 1) * studentsPerPage).toString());
    params.append('limit', studentsPerPage.toString());

    const data = await getStudents(Object.fromEntries(params.entries())); // Pass params as object
    students.value = data.records;
    totalStudents.value = data.total;
  } catch (error) {
    // Snackbar message handled in composable
    students.value = [];
    totalStudents.value = 0;
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchStudents();
  }
};


const fetchBuildingsTree = async () => {
  try {
    const data = await getBuildingsFullTree();
    buildingsTree.value = data as Building[];
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadBuildingData'), type: 'error' });
  }
};

const openModal = (mode: 'create' | 'edit', student: any = {}) => {
    modalMode.value = mode;
  if (mode === 'create') {
    editableStudent.value = { full_name: '', student_id_number: '', class_name: '', bed_id: null };
    originalBedId.value = null;
  } else {
    editableStudent.value = { ...student, bed_id: student.bed?.id || null };
    originalBedId.value = student.bed?.id || null;
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const handleSave = async () => {
  const isEdit = modalMode.value === 'edit';
  
  try {
    let savedStudent;
    if (isEdit) {
      const studentDataToUpdate = {
        student_id_number: editableStudent.value.student_id_number,
        full_name: editableStudent.value.full_name,
        class_name: editableStudent.value.class_name,
        gender: editableStudent.value.gender,
        identity_status: editableStudent.value.identity_status,
        is_foreign_student: editableStudent.value.is_foreign_student,
        enrollment_status: editableStudent.value.enrollment_status,
        remarks: editableStudent.value.remarks,
        license_plate: editableStudent.value.license_plate,
        contract_info: editableStudent.value.contract_info,
        temp_card_number: editableStudent.value.temp_card_number,
      };
      savedStudent = await updateStudent(editableStudent.value.id, studentDataToUpdate);

      if (editableStudent.value.bed_id !== originalBedId.value) {
        await assignBed(savedStudent.id, editableStudent.value.bed_id);
      }

    } else {
      savedStudent = await createStudent(editableStudent.value);
    }

    // Snackbar messages are now handled within useStudents composable
    await fetchStudents();
    closeModal();
  } catch (error: any) {
    // Snackbar messages are now handled within useStudents composable
  }
};

const handleDelete = async (id: string) => {
  if (!confirm(t('confirm.deleteStudent'))) return;

  try {
    await deleteStudent(id);
    // Snackbar message is now handled within useStudents composable
    await fetchStudents();
  } catch (error) {
    // Snackbar message is now handled within useStudents composable
  }
};

watch(searchQuery, debounce(() => {
  currentPage.value = 1;
  fetchStudents();
}, 300));

onMounted(() => {
  fetchStudents();
  fetchBuildingsTree();
});
</script>