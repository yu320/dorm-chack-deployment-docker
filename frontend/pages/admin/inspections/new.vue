<template>
  <div class="max-w-4xl mx-auto space-y-6 p-4 sm:p-6 lg:p-8 dark:text-gray-200">
    <!-- Header Card -->
    <div class="bg-white dark:bg-gray-800 p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
      <h1 class="text-3xl font-bold text-gray-800 dark:text-white text-center">{{ $t('inspection.newTitle') }}</h1>
      <p class="text-gray-600 dark:text-gray-400 mt-2 text-center">{{ $t('admin.newAdminInspectionDescription') }}</p>
    </div>

    <!-- Inspection Items -->
    <div class="space-y-6">
      <div v-for="(item, index) in inspectionDetails" :key="item.item_id" class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700 transition-all duration-300">
        <h3 class="text-xl font-semibold text-gray-900 dark:text-white">{{ $t(`items.${items.find(i => i.id === item.item_id)?.name.toLowerCase()}`) }}</h3>
        
        <div class="mt-4">
          <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('dashboard.status') }}</label>
          <div class="flex flex-wrap gap-3">
            <label v-for="status in itemStatuses" :key="status" class="flex items-center cursor-pointer">
              <input type="radio" :name="`status-${item.item_id}`" :value="status" v-model="item.status" class="sr-only">
              <div 
                class="px-4 py-2 rounded-full text-sm font-semibold transition-all duration-200 border"
                :class="{
                  'bg-green-100 dark:bg-green-800/30 border-green-300 dark:border-green-700 text-green-800 dark:text-green-300 ring-2 ring-green-500': item.status === status && status === 'ok',
                  'bg-yellow-100 dark:bg-yellow-800/30 border-yellow-300 dark:border-yellow-700 text-yellow-800 dark:text-yellow-300 ring-2 ring-yellow-500': item.status === status && status === 'damaged',
                  'bg-red-100 dark:bg-red-800/30 border-red-300 dark:border-red-700 text-red-800 dark:text-red-300 ring-2 ring-red-500': item.status === status && status === 'missing',
                  'bg-gray-50 dark:bg-gray-700 border-gray-200 dark:border-gray-600 text-gray-600 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-600': item.status !== status
                }"
              >
                {{ $t(`inspection.status.${status}`) }}
              </div>
            </label>
          </div>
        </div>

        <div v-if="item.status !== 'ok'" class="mt-4 space-y-4">
          <div>
            <label :for="`comment-${item.item_id}`" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('inspection.comment') }}</label>
            <textarea :id="`comment-${item.item_id}`" v-model="item.comment" rows="3" class="mt-1 block w-full border border-gray-300 dark:border-gray-600 rounded-lg shadow-sm py-2 px-3 bg-white dark:bg-gray-700 focus:outline-none focus:ring-primary-500 focus:border-primary-500"></textarea>
          </div>
          <div>
            <label :for="`photo-${item.item_id}`" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('inspection.photo') }}</label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 dark:border-gray-600 border-dashed rounded-md">
              <div class="space-y-1 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="flex text-sm text-gray-600 dark:text-gray-400">
                  <label :for="`photo-upload-${item.item_id}`" class="relative cursor-pointer bg-white dark:bg-gray-700 rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                    <span>{{ $t('inspection.uploadAFile') }}</span>
                    <input :id="`photo-upload-${item.item_id}`" @change="handlePhotoUpload($event, index)" type="file" class="sr-only" accept="image/*">
                  </label>
                  <p class="pl-1">{{ $t('inspection.orDragAndDrop') }}</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-400">{{ $t('inspection.fileTypes') }}</p>
              </div>
            </div>
            <div v-if="item.photos.length > 0" class="mt-4">
              <p class="text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">{{ $t('inspection.preview') }}</p>
              <img :src="item.photos[0].file_content" :alt="$t('inspection.photoPreview')" class="max-w-xs h-auto rounded-lg shadow-md border border-gray-200 dark:border-gray-600">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Signature -->
    <div class="bg-white dark:bg-gray-800 p-6 sm:p-8 rounded-2xl shadow-lg border border-gray-200 dark:border-gray-700">
      <h2 class="text-2xl font-bold text-gray-800 dark:text-white mb-4">{{ $t('inspection.studentSignature') }}</h2>
      <div class="border-2 border-dashed dark:border-gray-600 rounded-lg bg-gray-50 dark:bg-gray-900/50">
        <vue-signature-pad :key="theme" ref="signaturePad" width="100%" height="200px" :options="{ penColor: theme === 'dark' ? '#FFF' : '#000' }" />
      </div>
      <div class="flex justify-end mt-4">
        <button @click="clearSignature" class="px-4 py-2 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-200 dark:bg-gray-600 rounded-md hover:bg-gray-300 dark:hover:bg-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
          {{ $t('inspection.clearSignature') }}
        </button>
      </div>
    </div>

    <!-- Submission -->
    <div class="flex justify-center pt-4">
      <button @click="submitInspection" class="w-full max-w-md px-8 py-4 text-lg font-semibold text-white bg-primary-600 rounded-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 shadow-lg transform hover:scale-105 transition-transform duration-200">
        {{ $t('inspection.submitReport') }}
      </button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useRouter, useRoute } from 'vue-router';
import { useTheme } from '~/composables/useTheme';
import VueSignaturePad from 'vue3-signature';
import { useI18n } from 'vue-i18n';

const { t } = useI18n();

interface InspectionItem {
  id: string;
  name: string;
  description: string;
  is_active: boolean;
}

interface PhotoCreate {
  file_content: string;
  file_name: string;
}

interface InspectionDetailCreate {
  item_id: string;
  status: 'ok' | 'damaged' | 'missing';
  comment: string | null;
  photos: PhotoCreate[];
}

definePageMeta({
  middleware: [async (to, from) => {
    const { hasPermission } = useAuth();
    if (!hasPermission('inspections:submit')) {
      return navigateTo('/');
    }
  }],
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const router = useRouter();
const route = useRoute();
const { theme } = useTheme();

const items = ref<InspectionItem[]>([]);
const inspectionDetails = ref<InspectionDetailCreate[]>([]);
const itemStatuses = ['ok', 'damaged', 'missing'];
const signaturePad = ref(null);

const { target_type, target_id } = route.query;

const fetchItems = async () => {
  try {
    const response: any = await apiFetch('/api/v1/items/');
    // Handle paginated response { total: ..., records: [...] }
    items.value = response.records || response.items || (Array.isArray(response) ? response : []);
    
    // Initialize inspectionDetails based on fetched items
    inspectionDetails.value = items.value.map(item => ({
      item_id: item.id,
      status: 'ok',
      comment: null,
      photos: [],
    }));
  } catch (error) {
    console.error("Failed to fetch items:", error);
    showSnackbar(t('snackbar.failedToLoadInspectionItems'), 'error');
  }
};

const handlePhotoUpload = (event: Event, index: number) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files[0]) {
    const file = target.files[0];
    const reader = new FileReader();
    reader.onload = (e) => {
      inspectionDetails.value[index].photos = [{
        file_content: e.target?.result as string,
        file_name: file.name,
      }];
    };
    reader.readAsDataURL(file);
  }
};

const clearSignature = () => {
  (signaturePad.value as any)?.clear();
};

const submitInspection = async () => {
  if (!signaturePad.value) {
    showSnackbar(t('snackbar.signaturePadNotReady'), 'error');
    return;
  }
  const signatureData = (signaturePad.value as any).save();

  if (!signatureData) {
    showSnackbar(t('snackbar.provideSignature'), 'error');
    return;
  }

  let student_id: string | null = null;
  let room_id: number | null = null;

  if (target_type === 'student') {
    student_id = target_id as string;
    const student = await apiFetch(`/api/v1/students/${student_id}`);
    if (student && student.bed && student.bed.room) {
      room_id = student.bed.room.id;
    }
  } else if (target_type === 'room') {
    room_id = Number(target_id);
    // For a room inspection, we might not have a specific student.
    // The backend should be able to handle this.
  } else if (target_type === 'household') {
    // For a household inspection, we might not have a specific student or room.
    // The backend should be able to handle this.
  }
  
  if (!student_id && !room_id) {
      showSnackbar({ message: 'Cannot determine student or room for inspection.', type: 'error' });
      return;
  }

  const payload = {
    details: inspectionDetails.value,
    signature_base64: signatureData,
    student_id: student_id,
    room_id: room_id,
  };

  console.log('Submitting payload:', payload); // Debug log

  try {
    await apiFetch('/api/v1/inspections/', {
      method: 'POST',
      body: payload,
    });
    showSnackbar(t('snackbar.inspectionSubmitted'), 'success');
    router.push('/admin/inspections'); // Redirect to admin inspections list
  } catch (error: any) {
    console.error('Submit Error:', error.data || error); // Debug log
    const errorMessage = error.data?.detail || t('snackbar.failedToSubmitInspection');
    showSnackbar(errorMessage, 'error');
  }
};

onMounted(() => {
  fetchItems();
});
</script>
