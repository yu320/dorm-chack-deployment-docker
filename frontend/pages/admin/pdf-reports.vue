<template>
  <div class="p-4 sm:p-6">
    <div class="max-w-7xl mx-auto">
      <div v-if="initialLoading" class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <SkeletonLoader />
      </div>
      <div v-else class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.pdfReports.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ $t('admin.pdfReports.description') }}
        </p>

        <div class="space-y-6">
          <div>
            <label for="report-type" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.pdfReports.reportTypeLabel') }}</label>
            <select id="report-type" v-model="reportType" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option value="all">{{ $t('admin.pdfReports.allInspections') }}</option>
              <option value="building">{{ $t('admin.pdfReports.inspectionsByBuilding') }}</option>
              <option value="student">{{ $t('admin.pdfReports.studentDamageReport') }}</option>
            </select>
          </div>

          <!-- Building Selector (conditionally rendered) -->
          <div v-if="reportType === 'building'">
            <label for="building-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.roomManagement.buildings') }}</label>
            <select id="building-select" v-model="selectedBuildingId" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option :value="null">{{ $t('admin.selectBuildingPrompt') }}</option>
              <option v-for="building in buildings" :key="building.id" :value="building.id">{{ building.name }}</option>
            </select>
          </div>

          <!-- Student Selector (conditionally rendered) -->
          <div v-if="reportType === 'student'">
            <label for="student-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.userManagement.username') }}</label>
            <select id="student-select" v-model="selectedStudentId" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option :value="null">{{ $t('admin.filterByStudent') }}</option>
              <option v-for="student in students" :key="student.id" :value="student.id">{{ student.full_name }} ({{ student.student_id_number }})</option>
            </select>
          </div>

          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label for="start-date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.pdfReports.startDateLabel') }}</label>
              <input type="date" name="start-date" id="start-date" v-model="startDate" class="mt-1 block w-full sm:text-sm border-gray-300 rounded-md">
            </div>
            <div>
              <label for="end-date" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.pdfReports.endDateLabel') }}</label>
              <input type="date" name="end-date" id="end-date" v-model="endDate" class="mt-1 block w-full sm:text-sm border-gray-300 rounded-md">
            </div>
          </div>
        </div>

        <div class="mt-6">
          <button type="button" @click="generatePdf" :disabled="pdfLoading" class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed transition-transform active:scale-95">
            <span v-if="pdfLoading">{{ $t('loading') }}</span>
            <span v-else>{{ $t('admin.pdfReports.generatePdfButton') }}</span>
          </button>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import type { Building, Student } from '~/types';
import SkeletonLoader from '~/components/common/SkeletonLoader.vue';

definePageMeta({
  permission: 'view_all_records',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const reportType = ref<'all' | 'building' | 'student'>('all');
const selectedBuildingId = ref<number | null>(null);
const selectedStudentId = ref<string | null>(null);
const startDate = ref<string>('');
const endDate = ref<string>('');
const buildings = ref<Building[]>([]);
const students = ref<Student[]>([]);
const pdfLoading = ref(false);
const initialLoading = ref(true);

const fetchBuildings = async () => {
  try {
    const response = await apiFetch('/api/v1/buildings');
    buildings.value = response as Building[];
  } catch (error) {
    // console.error('Failed to fetch buildings:', error);
    showSnackbar({ message: t('snackbar.failedToLoadData'), type: 'error' });
  }
};

const fetchStudents = async () => {
  try {
    const response = await apiFetch('/api/v1/students');
    students.value = response as Student[];
  } catch (error) {
    // console.error('Failed to fetch students:', error);
    showSnackbar({ message: t('snackbar.failedToLoadStudents'), type: 'error' });
  }
};

const generatePdf = async () => {
  pdfLoading.value = true;
  try {
    const queryParams = new URLSearchParams();
    queryParams.append('report_type', reportType.value);

    if (reportType.value === 'building' && selectedBuildingId.value) {
      queryParams.append('building_id', selectedBuildingId.value.toString());
    } else if (reportType.value === 'student' && selectedStudentId.value) {
      queryParams.append('student_id', selectedStudentId.value);
    }

    if (startDate.value) {
      queryParams.append('start_date', startDate.value);
    }
    if (endDate.value) {
      queryParams.append('end_date', endDate.value);
    }

    const response = await apiFetch(`/api/v1/reports/pdf/inspections?${queryParams.toString()}`, {
      method: 'GET',
      responseType: 'blob', // Important for handling binary data
    });

    // Create a Blob from the PDF data
    const blob = new Blob([response], { type: 'application/pdf' });
    
    // Create a link element and trigger download
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `inspection_report_${Date.now()}.pdf`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    showSnackbar({ message: t('admin.pdfReports.generatePdfSuccess'), type: 'success' });

  } catch (error: any) {
    // console.error('Failed to generate PDF:', error);
    if (error.response && error.response.status === 401) {
      showSnackbar({ message: t('snackbar.loginFailed'), type: 'error' });
      // Redirect to login page if needed, or let the user manually login
      navigateTo('/login');
    } else {
      const errorMessage = error.response?._data?.detail || t('admin.pdfReports.generatePdfFailed');
      showSnackbar({ message: errorMessage, type: 'error' });
    }
  } finally {
    pdfLoading.value = false;
  }
};

onMounted(async () => {
  try {
    await Promise.all([fetchBuildings(), fetchStudents()]);
  } finally {
    initialLoading.value = false;
  }
});

// Reset selected building/student when report type changes
watch(reportType, (newType) => {
  if (newType !== 'building') {
    selectedBuildingId.value = null;
  }
  if (newType !== 'student') {
    selectedStudentId.value = null;
  }
});
</script>