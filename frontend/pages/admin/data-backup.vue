<template>
  <div class="p-4 sm:p-6">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.dataBackup.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ $t('admin.dataBackup.description') }}
        </p>

        <div class="space-y-8">
          <!-- Export Section -->
          <div>
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">{{ $t('admin.dataBackup.exportSectionTitle') }}</h2>
            <p class="text-gray-500 dark:text-gray-400 mb-4">
              {{ $t('admin.dataBackup.exportDescription') }}
            </p>
            <button
              @click="exportData"
              :disabled="loading"
              class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
            >
              <span v-if="loading">{{ $t('loading') }}</span>
              <span v-else>{{ $t('admin.dataBackup.exportButton') }}</span>
            </button>
          </div>

          <!-- Import Section -->
          <div>
            <h2 class="text-xl font-semibold text-gray-800 dark:text-gray-200 mb-3">{{ $t('admin.dataBackup.importSectionTitle') }}</h2>
            <p class="text-gray-500 dark:text-gray-400 mb-4">
              {{ $t('admin.dataBackup.importDescription') }}
            </p>
            <div class="flex items-center space-x-4">
              <label class="block">
                <span class="sr-only">{{ $t('admin.dataBackup.importFileLabel') }}</span>
                <input
                  type="file"
                  @change="handleFileChange"
                  accept=".json"
                  class="block w-full text-sm text-gray-500
                    file:mr-4 file:py-2 file:px-4
                    file:rounded-full file:border-0
                    file:text-sm file:font-semibold
                    file:bg-primary-50 file:text-primary-700
                    hover:file:bg-primary-100 disabled:cursor-not-allowed"
                  :disabled="loading"
                />
              </label>
              <button
                @click="importData"
                :disabled="!selectedFile || loading"
                class="bg-red-600 hover:bg-red-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed"
              >
                <span v-if="loading">{{ $t('loading') }}</span>
                <span v-else>{{ $t('admin.dataBackup.importButton') }}</span>
              </button>
            </div>
            <p v-if="selectedFile" class="mt-2 text-sm text-gray-500 dark:text-gray-400">Selected file: {{ selectedFile.name }}</p>
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

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const selectedFile = ref<File | null>(null);
const loading = ref(false);

const handleFileChange = (event: Event) => {
  const input = event.target as HTMLInputElement;
  if (input.files && input.files[0]) {
    selectedFile.value = input.files[0];
  } else {
    selectedFile.value = null;
  }
};

const exportData = async () => {
  loading.value = true;
  try {
    const response = await apiFetch('/api/v1/backup/export');

    const blob = new Blob([JSON.stringify(response, null, 2)], { type: 'application/json' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.setAttribute('download', `system_backup_${new Date().toISOString().split('T')[0]}.json`);
    document.body.appendChild(link);
    link.click();
    link.remove();
    window.URL.revokeObjectURL(url);

    showSnackbar({ message: t('admin.dataBackup.exportSuccess'), type: 'success' });
  } catch (error: any) {

    const errorMessage = error.response?._data?.detail || t('admin.dataBackup.exportFailed');
    showSnackbar({ message: errorMessage, type: 'error' });
  } finally {
    loading.value = false;
  }
};

const importData = async () => {
  if (!selectedFile.value) {
    showSnackbar({ message: t('admin.dataBackup.selectFilePrompt'), type: 'warning' }); // New i18n key
    return;
  }

  if (!confirm(t('admin.dataBackup.importConfirm'))) {
    return;
  }

  loading.value = true;
  try {
    const formData = new FormData();
    formData.append('file', selectedFile.value);

    await apiFetch('/api/v1/backup/import', {
      method: 'POST',
      body: formData,
      headers: {
        // No 'Content-Type' header needed for FormData; browser sets it automatically with boundary
      },
    });

    showSnackbar({ message: t('admin.dataBackup.importSuccess'), type: 'success' });
    selectedFile.value = null; // Clear selected file
  } catch (error: any) {

    const errorMessage = error.response?._data?.detail || t('admin.dataBackup.importFailed');
    showSnackbar({ message: errorMessage, type: 'error' });
  } finally {
    loading.value = false;
  }
};
</script>