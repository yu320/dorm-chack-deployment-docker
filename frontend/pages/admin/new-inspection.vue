<template>
  <div class="max-w-5xl mx-auto space-y-6 p-4 sm:p-6 lg:p-8 dark:text-gray-200 pb-24">
    <!-- Header -->
    <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">{{ $t('admin.newAdminInspectionTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2">{{ $t('admin.newAdminInspectionDescription') }}</p>

      <!-- Target Selection -->
      <div class="mt-6 space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.newAdminInspectionTargetType') }}</label>
          <div class="mt-2 flex space-x-4">
            <label v-for="type in targetTypes" :key="type.value" class="flex items-center cursor-pointer">
              <input type="radio" :value="type.value" v-model="selectedTargetType" class="focus:ring-primary-500 h-4 w-4 text-primary-600 border-gray-300">
              <span class="ml-2 text-sm text-gray-700 dark:text-gray-300">{{ type.label }}</span>
            </label>
          </div>
        </div>

        <div v-if="selectedTargetType">
          <label for="target" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.newAdminInspectionSelectTarget') }}</label>
          <div class="mt-1">
            <select id="target" v-model="selectedTargetId" class="block w-full pl-3 pr-10 py-2 text-base border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 rounded-md focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm">
              <option v-if="loadingTargets" value="">{{ $t('loading') }}</option>
              <option v-for="option in targetOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </option>
            </select>
          </div>
        </div>
        
        <button v-if="selectedTargetType !== 'student'" @click="loadBatchStudents" :disabled="!selectedTargetId || loadingList" class="mt-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50">
          {{ loadingList ? $t('loading') : $t('admin.loadStudents') || 'Load Students' }}
        </button>
      </div>
    </div>

    <!-- Batch Inspection List (For Room/Household) -->
    <div v-if="selectedTargetType !== 'student' && studentsList.length > 0" class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">
          {{ $t('admin.studentsList') || 'Students List' }} ({{ studentsList.length }})
        </h2>
        <div class="text-sm text-gray-500">
          {{ $t('admin.batchInspectionHint') || 'Default status is OK. Expand to mark issues.' }}
        </div>
      </div>

      <div v-for="(entry, sIndex) in studentsList" :key="entry.student.id" class="bg-white dark:bg-gray-800 rounded-lg shadow border border-gray-200 dark:border-gray-700 overflow-hidden">
        <!-- Student Header / Accordion Toggle -->
        <div @click="entry.expanded = !entry.expanded" class="p-4 flex justify-between items-center cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
          <div class="flex items-center space-x-4">
            <div class="h-10 w-10 rounded-full bg-primary-100 dark:bg-primary-900/50 flex items-center justify-center text-primary-600 dark:text-primary-400 font-bold">
              {{ entry.student.full_name.charAt(0) }}
            </div>
            <div>
              <p class="font-medium text-gray-900 dark:text-white">{{ entry.student.full_name }}</p>
              <p class="text-sm text-gray-500 dark:text-gray-400">{{ entry.student.student_id_number }} / Bed: {{ entry.student.bed?.bed_number || '-' }}</p>
            </div>
          </div>
          <div class="flex items-center space-x-4">
            <span v-if="hasIssues(entry)" class="px-2 py-1 text-xs font-semibold rounded-full bg-red-100 text-red-800 dark:bg-red-900/50 dark:text-red-300">
              {{ $t('inspection.status.damaged') }} / {{ $t('inspection.status.missing') }}
            </span>
            <span v-else class="px-2 py-1 text-xs font-semibold rounded-full bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300">
              {{ $t('inspection.status.ok') }}
            </span>
            <svg class="w-5 h-5 text-gray-400 transform transition-transform" :class="{'rotate-180': entry.expanded}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
          </div>
        </div>

        <!-- Detailed Inspection Form (Collapsible) -->
        <div v-show="entry.expanded" class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/30">
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div v-for="(item, iIndex) in entry.details" :key="item.item_id" class="bg-white dark:bg-gray-800 p-4 rounded-md border border-gray-200 dark:border-gray-600">
              <h4 class="font-medium text-gray-900 dark:text-white mb-2">{{ $t(`items.${itemsMap[item.item_id]?.name.toLowerCase()}`) }}</h4>
              
              <!-- Status Radios -->
              <div class="flex space-x-2 mb-3">
                <button v-for="status in ['ok', 'damaged', 'missing']" :key="status" 
                  @click="item.status = status"
                  class="px-3 py-1 text-xs rounded-full border transition-colors"
                  :class="{
                    'bg-green-100 border-green-300 text-green-800': item.status === status && status === 'ok',
                    'bg-yellow-100 border-yellow-300 text-yellow-800': item.status === status && status === 'damaged',
                    'bg-red-100 border-red-300 text-red-800': item.status === status && status === 'missing',
                    'bg-white border-gray-300 text-gray-600': item.status !== status
                  }"
                >
                  {{ $t(`inspection.status.${status}`) }}
                </button>
              </div>

              <!-- Comment & Photo (Only if not OK) -->
              <div v-if="item.status !== 'ok'" class="space-y-3">
                <textarea v-model="item.comment" rows="2" :placeholder="$t('inspection.comment')" class="w-full text-sm border-gray-300 rounded-md"></textarea>
                <!-- Simplified Photo Upload for Batch Mode -->
                <!-- Ideally reuse a PhotoUpload component -->
                <input type="file" @change="handleBatchPhotoUpload($event, sIndex, iIndex)" accept="image/*" class="text-xs">
                <div v-if="item.photos.length > 0" class="text-xs text-green-600">
                  {{ item.photos.length }} photo(s) selected
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Batch Submission -->
      <div class="fixed bottom-0 left-0 right-0 p-4 bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 shadow-lg flex justify-end items-center space-x-4 z-50">
        <span class="text-sm text-gray-500">{{ studentsList.length }} {{ $t('admin.students') }}</span>
        <button @click="submitBatchInspection" :disabled="submitting" class="px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white font-bold rounded-lg disabled:opacity-50">
          {{ submitting ? $t('loading') : $t('admin.submitBatch') || 'Submit All' }}
        </button>
      </div>
    </div>

    <!-- Single Student Mode (Direct Redirect) -->
    <div v-else-if="selectedTargetType === 'student'" class="mt-6">
      <button @click="startSingleInspection" :disabled="!selectedTargetId || loading" class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed">
        <span v-if="loading">{{ $t('loading') }}</span>
        <span v-else>{{ $t('admin.newAdminInspectionStartInspection') }}</span>
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive } from 'vue';
import { useI18n } from 'vue-i18n';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import Compressor from 'compressorjs';

definePageMeta({
  permission: 'inspections:submit',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const router = useRouter();
const localePath = useLocalePath();

const targetTypes = computed(() => [
  { label: t('admin.newAdminInspectionStudent'), value: 'student' },
  { label: t('admin.newAdminInspectionRoom'), value: 'room' },
  { label: t('admin.newAdminInspectionHousehold'), value: 'household' },
]);

const selectedTargetType = ref('student');
const selectedTargetId = ref<string | number>('');
const loadingTargets = ref(false);
const loading = ref(false);
const loadingList = ref(false);
const submitting = ref(false);

const allStudents = ref<any[]>([]);
const allRooms = ref<any[]>([]);
const allHouseholds = ref<string[]>([]);
const items = ref<any[]>([]);
const itemsMap = computed(() => {
  const map: Record<string, any> = {};
  items.value.forEach(i => map[i.id] = i);
  return map;
});

// Batch List State
interface BatchEntry {
  student: any;
  details: any[];
  signature_base64: string | null;
  expanded: boolean;
}
const studentsList = ref<BatchEntry[]>([]);

const targetOptions = computed(() => {
  switch (selectedTargetType.value) {
    case 'student':
      return allStudents.value.map(s => ({ label: `${s.full_name} (${s.student_id_number})`, value: s.id }));
    case 'room':
      return allRooms.value.map(r => ({ label: r.room_number, value: r.id }));
    case 'household':
      return allHouseholds.value.map(h => ({ label: h, value: h }));
    default:
      return [];
  }
});

const fetchTargets = async () => {
  loadingTargets.value = true;
  selectedTargetId.value = '';
  studentsList.value = []; // Reset list
  try {
    if (selectedTargetType.value === 'student') {
      const response: any = await apiFetch('/api/v1/students/');
      allStudents.value = response.records || response.students || [];
    } else if (selectedTargetType.value === 'room') {
      const response: any = await apiFetch('/api/v1/rooms/');
      allRooms.value = response.records || response.rooms || [];
    } else if (selectedTargetType.value === 'household') {
      const response: any = await apiFetch('/api/v1/rooms/');
      const rooms = response.records || response.rooms || [];
      const households = new Set(rooms.map((r: any) => r.household).filter(Boolean));
      allHouseholds.value = Array.from(households) as string[];
    }
    
    // Pre-fetch items for batch logic
    if (items.value.length === 0) {
        const itemsRes: any = await apiFetch('/api/v1/items/');
        items.value = itemsRes.records || itemsRes.items || (Array.isArray(itemsRes) ? itemsRes : []);
    }
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToLoadTargets'), type: 'error' });
  } finally {
    loadingTargets.value = false;
  }
};

watch(selectedTargetType, fetchTargets, { immediate: true });

// Load students for batch inspection (Room/Household)
const loadBatchStudents = async () => {
    loadingList.value = true;
    studentsList.value = [];
    try {
        let studentsUrl = '/api/v1/students/';
        if (selectedTargetType.value === 'room') {
            studentsUrl += `?room_id=${selectedTargetId.value}`;
        } else if (selectedTargetType.value === 'household') {
            studentsUrl += `?household=${selectedTargetId.value}`;
        }

        const response: any = await apiFetch(studentsUrl);
        const students = response.records || response.students || [];

        if (students.length === 0) {
            showSnackbar({ message: t('admin.noStudentsFound'), type: 'warning' });
        }

        // Init state for each student
        studentsList.value = students.map((s: any) => ({
            student: s,
            details: items.value.map(i => ({
                item_id: i.id,
                status: 'ok',
                comment: '',
                photos: []
            })),
            signature_base64: null,
            expanded: false
        }));

    } catch (error) {
        console.error(error);
        showSnackbar({ message: t('snackbar.failedToLoadStudents'), type: 'error' });
    } finally {
        loadingList.value = false;
    }
};

const hasIssues = (entry: BatchEntry) => {
    return entry.details.some(d => d.status !== 'ok');
};

const handleBatchPhotoUpload = (event: Event, sIndex: number, iIndex: number) => {
    const target = event.target as HTMLInputElement;
    if (target.files && target.files[0]) {
        const file = target.files[0];
        new Compressor(file, {
            quality: 0.6,
            maxWidth: 800,
            success(result) {
                const reader = new FileReader();
                reader.onload = (e) => {
                    studentsList.value[sIndex].details[iIndex].photos = [{
                        file_content: e.target?.result as string,
                        file_name: result.name
                    }];
                };
                reader.readAsDataURL(result);
            },
            error(err) {
                console.error(err.message);
            },
        });
    }
};

const submitBatchInspection = async () => {
    submitting.value = true;
    try {
        const payload = {
            inspections: studentsList.value.map(entry => ({
                student_id: entry.student.id,
                room_id: entry.student.bed?.room?.id, // Get from student info
                details: entry.details,
                signature_base64: null // Admin batch typically has no student signature
            }))
        };

        await apiFetch('/api/v1/inspections/batch', {
            method: 'POST',
            body: payload
        });

        showSnackbar({ message: 'Batch inspection submitted successfully!', type: 'success' }); // Need i18n
        router.push('/admin/inspections');
    } catch (error: any) {
        console.error('Batch submit error:', error);
        showSnackbar({ message: 'Failed to submit batch inspection.', type: 'error' });
    } finally {
        submitting.value = false;
    }
};

const startSingleInspection = () => {
  if (!selectedTargetId.value) return;
  
  const query: { target_type: string; target_id: string | number } = {
    target_type: selectedTargetType.value,
    target_id: selectedTargetId.value,
  };

  router.push(localePath({
    path: '/admin/inspections/new',
    query: query,
  }));
};
</script>