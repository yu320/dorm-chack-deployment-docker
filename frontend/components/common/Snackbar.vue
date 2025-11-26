<template>
  <div v-if="snackbar.visible" class="fixed bottom-5 right-5 z-50">
    <div
      :class="[
        'flex items-center justify-between w-full max-w-sm p-4 bg-white dark:bg-gray-800 shadow-lg rounded-lg pointer-events-auto ring-1 ring-black ring-opacity-5',
        colorClasses
      ]"
    >
      <div class="flex items-start">
        <div class="flex-shrink-0">
            <svg v-if="snackbar.type === 'success'" class="h-6 w-6 text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else-if="snackbar.type === 'error'" class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
            <svg v-else class="h-6 w-6 text-blue-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
        </div>
        <div class="ml-3 flex-1 pt-0.5">
          <p class="text-sm font-medium text-gray-900 dark:text-white">
            {{ snackbar.message }}
          </p>
        </div>
      </div>
      <div class="ml-4 flex-shrink-0 flex">
        <button @click="hideSnackbar" class="inline-flex text-gray-400 rounded-md hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500">
          <span class="sr-only">Close</span>
          <svg class="w-5 h-5" xmlns="http://www.w3.org/2000/svg" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useSnackbar } from '~/composables/useSnackbar';

const { snackbar, hideSnackbar } = useSnackbar();

const colorClasses = computed(() => {
  switch (snackbar.value.type) {
    case 'success':
      return 'border-l-4 border-green-500';
    case 'error':
      return 'border-l-4 border-red-500';
    case 'info':
    default:
      return 'border-l-4 border-blue-500';
  }
});
</script>
