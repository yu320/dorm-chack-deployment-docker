<template>
  <div v-if="record" class="max-w-4xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-3xl font-bold text-gray-800 dark:text-white">{{ $t('records.myRecordsTitle') }} #{{ record.id }}</h1>
        <div class="flex items-center space-x-4">
          <button @click="downloadPdf" class="text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" /></svg>
            {{ $t('records.downloadPdf') }}
          </button>
          <NuxtLink to="/admin/records" class="text-primary-600 dark:text-primary-400 hover:text-primary-800 dark:hover:text-primary-300 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
            {{ $t('records.backToMyRecords') }}
          </NuxtLink>
        </div>
      </div>
      <p class="text-gray-600 dark:text-gray-300 mt-2">{{ $t('records.detailedView') }}</p>
    </div>

    <!-- Inspection Summary -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('inspection.summary') }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ $t('inspection.studentName') }}:</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ record.student.full_name }}</p>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ $t('inspection.roomNumber') }}:</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ record.room.room_number }}</p>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ $t('dashboard.status') }}:</p>
          <p class="text-lg font-semibold" :class="statusColor(record.status)">{{ $t(`inspection.status.${record.status.toLowerCase()}`) }}</p>
        </div>
        <div class="bg-gray-50 dark:bg-gray-700/50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500 dark:text-gray-400">{{ $t('inspection.submittedAt') }}:</p>
          <p class="text-lg font-semibold text-gray-900 dark:text-white">{{ new Date(record.created_at).toLocaleString() }}</p>
        </div>
      </div>
    </div>

    <!-- Admin Actions -->
    <div v-if="hasPermission('update_any_record')" class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('admin.adminActions') }}</h2>
      <div class="space-y-6">
        <!-- Status Update -->
        <div>
          <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ $t('admin.updateStatus') }}</h3>
          <div class="flex items-center space-x-4">
            <select v-model="newStatus" class="block w-full max-w-xs border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500">
              <option v-for="status in availableStatuses" :key="status" :value="status">{{ $t('inspection.status.' + status) }}</option>
            </select>
            <button @click="updateStatus" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
              {{ $t('admin.update') }}
            </button>
          </div>
        </div>
        <!-- Email Report -->
        <div>
          <h3 class="text-lg font-semibold text-gray-700 dark:text-gray-300 mb-2">{{ $t('admin.emailReport') }}</h3>
          <div class="flex items-center space-x-4">
            <input type="email" v-model="recipientEmail" :placeholder="$t('admin.recipientEmailPlaceholder')" class="block w-full max-w-xs border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 text-gray-900 dark:text-white rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500">
            <button @click="emailReport" class="px-4 py-2 text-sm font-medium text-white bg-secondary-600 rounded-md hover:bg-secondary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-secondary-500">
              {{ $t('admin.sendEmail') }}
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Inspected Items -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('inspection.inspectionItems') }}</h2>
      <div class="space-y-6">
        <div v-for="detail in record.details" :key="detail.id" class="p-6 border border-gray-200 dark:border-gray-700 rounded-lg shadow-sm bg-gray-50 dark:bg-gray-700/50">
          <h3 class="text-xl font-semibold text-gray-800 dark:text-white">{{ $t(`items.${detail.item.name.toLowerCase()}`) }}</h3>
          <p class="text-gray-600 dark:text-gray-300">{{ $t('dashboard.status') }}: <span :class="detail.status === 'ok' ? 'text-green-500 dark:text-green-400' : 'text-red-500 dark:text-red-400'">{{ $t(`inspection.status.${detail.status.toLowerCase()}`) }}</span></p>
          <p v-if="detail.comment" class="text-gray-600 dark:text-gray-300 mt-1">{{ $t('inspection.comment') }}: {{ detail.comment }}</p>
          <div v-if="detail.photos && detail.photos.length > 0" class="mt-4 grid grid-cols-2 gap-4">
            <div v-for="photo in detail.photos" :key="photo.id">
              <img :src="getFullImageUrl(photo.file_path)" :alt="$t('inspection.photoFor', { itemName: detail.item.name })" class="max-w-xs h-auto rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Signature -->
    <div class="bg-white dark:bg-gray-800 p-8 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('inspection.studentSignature') }}</h2>
      <div class="border rounded-lg p-4 bg-gray-50 dark:bg-gray-700/50 flex justify-center items-center">
        <img v-if="record.signature" :src="record.signature" :alt="$t('inspection.studentSignature')" class="max-w-full h-auto rounded-md shadow-sm bg-white">
        <p v-else class="text-gray-500 dark:text-gray-400">{{ $t('inspection.noSignature') }}</p>
      </div>
    </div>
  </div>
  <div v-else class="text-center p-8 dark:text-gray-300">
    <p>{{ $t('loading') }}</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useTheme } from '~/composables/useTheme';

interface Photo {
  id: string;
  file_path: string;
}

interface Item {
  id: string;
  name: string;
}

interface Detail {
  id: string;
  item: Item;
  status: string;
  comment: string | null;
  photos: Photo[];
}

interface Student {
  id: string;
  full_name: string;
}

interface Room {
  id: number;
  room_number: string;
}

interface InspectionRecord {
  id: string;
  student: Student;
  room: Room;
  status: string;
  created_at: string;
  details: Detail[];
  signature: string | null;
}

const route = useRoute();
const { t } = useI18n();
const { apiFetch, hasPermission } = useAuth();
const { showSnackbar } = useSnackbar();
const config = useRuntimeConfig();
const { theme } = useTheme();

const record = ref<InspectionRecord | null>(null);
const newStatus = ref('');
const availableStatuses = ['pending', 'submitted', 'approved'];
const recipientEmail = ref('');

const fetchRecord = async () => {
  try {
    const recordId = route.params.id;
    const response = await apiFetch(`/api/v1/inspections/${recordId}`);
    record.value = response as InspectionRecord;
    newStatus.value = record.value.status;
  } catch (error) {
    console.error('Failed to fetch inspection record:', error);
    showSnackbar({ message: t('snackbar.failedToLoadRecord'), type: 'error' });
  }
};

const updateStatus = async () => {
  if (!record.value) return;
  try {
    await apiFetch(`/api/v1/inspections/${record.value.id}`, {
      method: 'PUT',
      body: { status: newStatus.value },
    });
    showSnackbar({ message: t('snackbar.statusUpdated'), type: 'success' });
    await fetchRecord(); // Refresh the record
  } catch (error) {
    console.error('Failed to update status:', error);
    showSnackbar({ message: t('snackbar.failedToUpdateStatus'), type: 'error' });
  }
};

const emailReport = async () => {
  if (!record.value || !recipientEmail.value) {
    showSnackbar({ message: t('snackbar.enterRecipientEmail'), type: 'error' });
    return;
  }
  try {
    await apiFetch(`/api/v1/inspections/${record.value.id}/email`, {
      method: 'POST',
      body: { recipient_email: recipientEmail.value },
    });
    showSnackbar({ message: t('snackbar.reportEmailed'), type: 'success' });
    recipientEmail.value = ''; // Clear the input
  } catch (error) {
    console.error('Failed to email report:', error);
    showSnackbar({ message: t('snackbar.failedToEmailReport'), type: 'error' });
  }
};

const downloadPdf = () => {
  if (!record.value) return;
  const pdfUrl = `${config.public.apiBase}/api/v1/inspections/${record.value.id}/pdf`;
  window.open(pdfUrl, '_blank');
};

const getFullImageUrl = (filePath: string) => {
  if (!filePath) return '';
  const cleanPath = filePath.startsWith('/') ? filePath.substring(1) : filePath;
  return `${config.public.apiBase}/api/v1/images/${cleanPath}`;
};

const statusColor = computed(() => (status: string) => {
  const isDark = theme.value === 'dark';
  switch (status) {
    case 'approved':
      return isDark ? 'text-green-400' : 'text-green-600';
    case 'submitted':
      return isDark ? 'text-yellow-400' : 'text-yellow-600';
    case 'pending':
      return isDark ? 'text-gray-400' : 'text-gray-600';
    default:
      return isDark ? 'text-white' : 'text-gray-900';
  }
});

onMounted(() => {
  fetchRecord();
});
</script>