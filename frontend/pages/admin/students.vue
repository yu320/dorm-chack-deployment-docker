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
        <input type="text" v-model="searchQuery" :placeholder="$t('admin.searchStudents')" class="w-full px-4 py-2 border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-lg focus:outline-none focus:ring-2 focus:ring-primary-500">
      </div>
      <div>
        <button @click="openModal('create')" class="bg-primary-600 hover:bg-primary-700 text-white font-bold py-2 px-4 rounded-lg shadow-md transition duration-300">
          {{ $t('admin.createStudent') }}
        </button>
      </div>
    </div>

    <!-- Students Table -->
    <div class="bg-white dark:bg-gray-800 rounded-lg shadow-lg overflow-hidden border border-gray-200 dark:border-gray-700">
      <div class="overflow-x-auto">
        <table class="min-w-full divide-y divide-gray-200 dark:divide-gray-700">
          <thead class="bg-gray-50 dark:bg-gray-700/50">
            <tr>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.fullName') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.studentId') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('admin.class') }}</th>
              <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 dark:text-gray-300 uppercase tracking-wider">{{ $t('dashboard.room') }}</th>
              <th scope="col" class="relative px-6 py-3"><span class="sr-only">{{ $t('admin.actions') }}</span></th>
            </tr>
          </thead>
          <tbody class="bg-white dark:bg-gray-800 divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="student in students" :key="student.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50">
              <td class="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900 dark:text-white">{{ student.full_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ student.student_id_number }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">{{ student.class_name }}</td>
              <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-500 dark:text-gray-400">
                {{ student.bed ? `${student.bed.room.room_number} / ${student.bed.bed_number}` : 'N/A' }}
              </td>
              <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                <a href="#" @click.prevent="openModal('edit', student)" class="text-primary-600 dark:text-primary-400 hover:text-primary-900 dark:hover:text-primary-300 mr-4">{{ $t('admin.edit') }}</a>
                <a href="#" @click.prevent="handleDelete(student.id)" class="text-red-600 dark:text-red-500 hover:text-red-900 dark:hover:text-red-400">{{ $t('admin.delete') }}</a>
              </td>
            </tr>
             <tr v-if="students.length === 0">
              <td colspan="5" class="px-6 py-4 text-center text-sm text-gray-500 dark:text-gray-400">{{ $t('admin.noStudentsFound') }}</td>
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
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="fullName" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.fullName') }}</label>
              <input type="text" v-model="editableStudent.full_name" id="fullName" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="studentId" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.studentId') }}</label>
              <input type="text" v-model="editableStudent.student_id_number" id="studentId" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="className" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.class') }}</label>
              <input type="text" v-model="editableStudent.class_name" id="className" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm">
            </div>
            <div>
              <label for="bedId" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.beds') }}</label>
              <NestedSelect
                v-model="editableStudent.bed_id"
                :options="buildingsTree"
                :loading="treeLoading"
                :original-bed-id="originalBedId"
                :placeholder="$t('admin.selectBed')"
              />
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
import NestedSelect from '~/components/common/NestedSelect.vue';
import { useI18n } from '#imports';

// Interfaces
interface Student {
  id: string;
  full_name: string;
  student_id_number: string;
  class_name: string;
  bed: {
    id: number;
    bed_number: string;
    room: {
      id: number;
      room_number: string;
    }
  } | null;
}

interface Building {
  id: number;
  name: string;
  rooms: {
    id: number;
    room_number: string;
    beds: {
      id: number;
      bed_number: string;
      status: string;
    }[];
  }[];
}

interface PaginatedStudentResponse {
  total: number;
  records: Student[];
}

definePageMeta({
  permission: 'manage_students',
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

// State
const students = ref<Student[]>([]);
const buildingsTree = ref<Building[]>([]);
const treeLoading = ref(false);
const loading = ref(false);
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

// Methods
const fetchStudents = async () => {
  loading.value = true;
  try {
    const params = new URLSearchParams();
    if (searchQuery.value) {
      params.append('full_name', searchQuery.value);
    }
    params.append('skip', ((currentPage.value - 1) * studentsPerPage).toString());
    params.append('limit', studentsPerPage.toString());

    const data = await apiFetch(`/api/v1/students/?${params.toString()}`) as PaginatedStudentResponse;
    students.value = data.records;
    totalStudents.value = data.total;
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadStudents'), type: 'error' });
    students.value = [];
    totalStudents.value = 0;
  } finally {
    loading.value = false;
  }
};

const changePage = (page: number) => {
  if (page > 0 && page <= totalPages.value) {
    currentPage.value = page;
    fetchStudents();
  }
};


const fetchBuildingsTree = async () => {
    treeLoading.value = true;
  try {
    const data = await apiFetch('/api/v1/buildings/full-tree/');
    buildingsTree.value = data as Building[];
  } catch (error) {
    showSnackbar(t('snackbar.failedToLoadBuildingData'), 'error');
  } finally {
    treeLoading.value = false;
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
      // For PUT, only send fields defined in the StudentUpdate schema
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
      savedStudent = await apiFetch(`/api/v1/students/${editableStudent.value.id}`, {
        method: 'PUT',
        body: studentDataToUpdate,
      });

      // If bed has changed, make a separate call to assign bed
      if (editableStudent.value.bed_id !== originalBedId.value) {
        await apiFetch(`/api/v1/students/${savedStudent.id}/assign-bed`, {
          method: 'PUT',
          body: { bed_id: editableStudent.value.bed_id },
        });
      }

    } else {
      // For POST, send the full object as defined by StudentCreate
      savedStudent = await apiFetch('/api/v1/students/', {
        method: 'POST',
        body: editableStudent.value,
      });
    }

    showSnackbar({ message: t(isEdit ? 'snackbar.studentUpdated' : 'snackbar.studentCreated'), type: 'success' });
    await fetchStudents();
    closeModal();
  } catch (error: any) {
    const errorMessage = error.data?.detail || t('snackbar.failedToSaveStudent');
    showSnackbar({ message: errorMessage, type: 'error' });
  }
};

const handleDelete = async (id: string) => {
  if (!confirm(t('confirm.deleteStudent'))) return;

  try {
    await apiFetch(`/api/v1/students/${id}`, { method: 'DELETE' });
    showSnackbar({ message: t('snackbar.studentDeleted'), type: 'success' });
    await fetchStudents();
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToDeleteStudent'), type: 'error' });
  }
};

// Watch for search query changes
watch(searchQuery, debounce(() => {
  currentPage.value = 1;
  fetchStudents();
}, 300));

onMounted(() => {
  fetchStudents();
  fetchBuildingsTree();
});
</script>
