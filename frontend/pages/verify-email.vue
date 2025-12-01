<template>
  <div class="relative flex items-center justify-center min-h-screen overflow-hidden bg-gray-100 dark:bg-gray-900">
    <!-- Dynamic Glow Effect -->
    <div class="absolute w-64 h-64 bg-primary-500 rounded-full -top-16 -left-16 dark:bg-primary-700 animate-pulse-slow mix-blend-multiply filter blur-xl opacity-70"></div>
    <div class="absolute w-64 h-64 bg-secondary-500 rounded-full -bottom-16 -right-16 dark:bg-secondary-700 animate-pulse-slow-delay mix-blend-multiply filter blur-xl opacity-70"></div>

    <div class="relative z-10 w-full max-w-md p-8 space-y-6 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/30 dark:border-gray-700/30 text-center">
      <h2 class="text-3xl font-bold text-gray-900 dark:text-white mb-4">
        Account Verification
      </h2>

      <!-- Loading State -->
      <div v-if="status === 'verifying'" class="flex flex-col items-center justify-center space-y-4">
        <div class="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600 dark:border-primary-400"></div>
        <p class="text-gray-600 dark:text-gray-300">Verifying your email...</p>
      </div>

      <!-- Success State -->
      <div v-else-if="status === 'success'" class="space-y-6">
        <div class="flex justify-center">
          <div class="rounded-full bg-green-100 p-3 dark:bg-green-900">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-green-600 dark:text-green-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7" />
            </svg>
          </div>
        </div>
        <p class="text-lg font-medium text-gray-900 dark:text-white">Email Verified!</p>
        <p class="text-gray-600 dark:text-gray-300">Your account has been successfully verified. You can now log in.</p>
        <NuxtLink
          to="/login"
          class="inline-flex justify-center w-full px-4 py-3 text-sm font-medium text-white transition duration-300 ease-in-out border border-transparent rounded-lg shadow-sm bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-primary-500 dark:hover:bg-primary-600"
        >
          Go to Login
        </NuxtLink>
      </div>

      <!-- Error State -->
      <div v-else-if="status === 'error'" class="space-y-6">
         <div class="flex justify-center">
          <div class="rounded-full bg-red-100 p-3 dark:bg-red-900">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 text-red-600 dark:text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
            </svg>
          </div>
        </div>
        <p class="text-lg font-medium text-red-600 dark:text-red-400">Verification Failed</p>
        <p class="text-gray-600 dark:text-gray-300">{{ errorMessage }}</p>
        <NuxtLink
          to="/login"
          class="inline-flex justify-center w-full px-4 py-3 text-sm font-medium text-white transition duration-300 ease-in-out border border-transparent rounded-lg shadow-sm bg-gray-600 hover:bg-gray-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-gray-500"
        >
          Back to Login
        </NuxtLink>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';

definePageMeta({
  layout: 'empty',
});

const route = useRoute();
const config = useRuntimeConfig();

type Status = 'verifying' | 'success' | 'error';
const status = ref<Status>('verifying');
const errorMessage = ref('Invalid or expired verification token.');

onMounted(async () => {
  const token = route.query.token;
  
  if (!token || typeof token !== 'string') {
    status.value = 'error';
    errorMessage.value = 'Missing verification token.';
    return;
  }

  try {
    // The API endpoint is GET /verify-email/{token}
    // We need to construct the URL correctly.
    // Assuming config.public.apiBase is the base URL for API (e.g., /api/v1/auth or just /api/v1)
    // Let's check reset-password usage:
    // await $fetch('/api/v1/auth/reset-password', { baseURL: config.public.apiBase ... })
    // This implies config.public.apiBase is likely just the host or empty if proxy?
    // Wait, if the path in $fetch is '/api/v1/...', then baseURL should be the domain.
    // Let's assume standard Nuxt usage.
    
    await $fetch(`/api/v1/auth/verify-email/${token}`, {
      baseURL: config.public.apiBase,
      method: 'GET',
    });

    status.value = 'success';
  } catch (error: any) {
    console.error('Verification error:', error);
    status.value = 'error';
    if (error.response && error.response._data && error.response._data.detail) {
      errorMessage.value = error.response._data.detail;
    }
  }
});
</script>

<style scoped>
.animate-pulse-slow {
  animation: pulse 4s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.animate-pulse-slow-delay {
  animation: pulse 5s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% {
    opacity: 0.7;
    transform: scale(1);
  }
  50% {
    opacity: 0.4;
    transform: scale(1.2);
  }
}
</style>