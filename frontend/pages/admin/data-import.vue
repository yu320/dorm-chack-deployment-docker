<template>
  <div class="p-4 sm:p-6">
    <div class="max-w-2xl mx-auto">
      <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.dataImport.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ $t('admin.dataImport.description') }}
        </p>

        <div class="space-y-6">
          <div>
            <label for="file-upload" class="block text-sm font-medium text-gray-700 dark:text-gray-300">
              {{ $t('admin.dataImport.fileLabel') }}
            </label>
            <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
              <div class="space-y-1 text-center">
                <svg class="mx-auto h-12 w-12 text-gray-400" stroke="currentColor" fill="none" viewBox="0 0 48 48" aria-hidden="true">
                  <path d="M28 8H12a4 4 0 00-4 4v20m32-12v8m0 0v8a4 4 0 01-4 4H12a4 4 0 01-4-4v-4m32-4l-3.172-3.172a4 4 0 00-5.656 0L28 28M8 32l9.172-9.172a4 4 0 015.656 0L28 28m0 0l4 4m4-24h8m-4-4v8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" />
                </svg>
                <div class="flex text-sm text-gray-600 dark:text-gray-400">
                  <label for="file-upload" class="relative cursor-pointer bg-white rounded-md font-medium text-primary-600 hover:text-primary-500 focus-within:outline-none focus-within:ring-2 focus-within:ring-offset-2 focus-within:ring-primary-500">
                    <span>{{ $t('admin.dataImport.uploadAFile') }}</span>
                    <input id="file-upload" name="file-upload" type="file" class="sr-only" @change="handleFileChange" accept=".csv, application/vnd.openxmlformats-officedocument.spreadsheetml.sheet, application/vnd.ms-excel">
                  </label>
                  <p class="pl-1">{{ $t('admin.dataImport.orDragAndDrop') }}</p>
                </div>
                <p class="text-xs text-gray-500 dark:text-gray-500">
                  {{ $t('admin.dataImport.fileTypes') }}
                </p>
              </div>
            </div>
            <p v-if="selectedFile" class="mt-2 text-sm text-gray-500 dark:text-gray-400">
              {{ $t('admin.dataImport.selectedFile') }}: {{ selectedFile.name }}
            </p>
          </div>
        </div>

        <div class="mt-6">
          <button @click="uploadFile" :disabled="!selectedFile || loading" class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed flex justify-center items-center">
            <svg v-if="loading" class="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            {{ loading ? $t('admin.dataImport.importing') : $t('admin.dataImport.importButton') }}
          </button>
        </div>

        <div v-if="importResult" class="mt-6 p-4 bg-gray-100 dark:bg-gray-700 rounded-lg">
          <h3 class="text-lg font-medium text-gray-900 dark:text-white">{{ $t('admin.dataImport.resultsTitle') }}</h3>
          <p class="mt-2 text-sm text-gray-600 dark:text-gray-300">{{ importResult.message }}</p>
          <div v-if="importResult.created" class="mt-2 text-sm">
            <p><strong>{{ $t('admin.dataImport.created') }}:</strong></p>
            <ul class="list-disc list-inside">
              <li v-for="(count, item) in importResult.created" :key="item">{{ item }}: {{ count }}</li>
            </ul>
          </div>
          <div v-if="importResult.updated" class="mt-2 text-sm">
            <p><strong>{{ $t('admin.dataImport.updated') }}:</strong></p>
            <ul class="list-disc list-inside">
              <li v-for="(count, item) in importResult.updated" :key="item">{{ item }}: {{ count }}</li>
            </ul>
          </div>
        </div>

      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';

definePageMeta({
  permission: 'manage_users',
});

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

const selectedFile = ref<File | null>(null);
const loading = ref(false);
const importResult = ref<any>(null);

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement;
  if (target.files && target.files.length > 0) {
    selectedFile.value = target.files[0];
    importResult.value = null;
  }
};

const uploadFile = async () => {
  if (!selectedFile.value) return;

  loading.value = true;
  importResult.value = null;
  const formData = new FormData();
  formData.append('file', selectedFile.value);

  try {
    const result = await apiFetch('/api/v1/import/upload', {
      method: 'POST',
      body: formData,
    });
    importResult.value = result;
    showSnackbar(result.message || t('admin.dataImport.importSuccess'), 'success');
  } catch (error: any) {
    const errorMessage = error.data?.detail || t('admin.dataImport.importFailed');
    showSnackbar(errorMessage, 'error');
    importResult.value = { message: errorMessage };
  } finally {
    loading.value = false;
  }
};
</script>