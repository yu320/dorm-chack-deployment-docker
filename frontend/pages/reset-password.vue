<template>
  <div class="relative flex items-center justify-center min-h-screen overflow-hidden bg-gray-100 dark:bg-gray-900">
    <!-- Dynamic Glow Effect -->
    <div class="absolute w-64 h-64 bg-primary-500 rounded-full -top-16 -left-16 dark:bg-primary-700 animate-pulse-slow mix-blend-multiply filter blur-xl opacity-70"></div>
    <div class="absolute w-64 h-64 bg-secondary-500 rounded-full -bottom-16 -right-16 dark:bg-secondary-700 animate-pulse-slow-delay mix-blend-multiply filter blur-xl opacity-70"></div>

    <div class="relative z-10 w-full max-w-md p-8 space-y-6 bg-white/60 dark:bg-gray-800/60 backdrop-blur-xl rounded-2xl shadow-2xl border border-white/30 dark:border-gray-700/30">
      <h2 class="text-3xl font-bold text-center text-gray-900 dark:text-white">
        Reset Your Password
      </h2>
      <form @submit.prevent="handleResetPassword" class="space-y-6">
        <div>
          <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">New Password</label>
          <div class="relative">
            <input
              id="new_password"
              name="new_password"
              :type="showNewPassword ? 'text' : 'password'"
              required
              v-model="newPassword"
              class="block w-full px-4 py-3 mt-1 border-gray-300 rounded-lg shadow-sm bg-white/80 dark:bg-gray-700/80 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 pr-10"
            />
            <button
              type="button"
              @click="showNewPassword = !showNewPassword"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5 text-gray-700 dark:text-gray-300 focus:outline-none"
            >
              <svg v-if="!showNewPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
        </div>
        <div>
          <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Confirm New Password</label>
          <div class="relative">
            <input
              id="confirm_password"
              name="confirm_password"
              :type="showConfirmPassword ? 'text' : 'password'"
              required
              v-model="confirmPassword"
              class="block w-full px-4 py-3 mt-1 border-gray-300 rounded-lg shadow-sm bg-white/80 dark:bg-gray-700/80 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500 pr-10"
            />
            <button
              type="button"
              @click="showConfirmPassword = !showConfirmPassword"
              class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5 text-gray-700 dark:text-gray-300 focus:outline-none"
            >
              <svg v-if="!showConfirmPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
              </svg>
            </button>
          </div>
        </div>
        
        <div>
          <button
            type="submit"
            :disabled="loading"
            class="flex justify-center w-full px-4 py-3 text-sm font-medium text-white transition duration-300 ease-in-out border border-transparent rounded-lg shadow-sm bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 dark:bg-primary-500 dark:hover:bg-primary-600 disabled:bg-primary-300 dark:disabled:bg-primary-800"
          >
            <span v-if="loading">Resetting...</span>
            <span v-else>Reset Password</span>
          </button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { useSnackbar } from '~/composables/useSnackbar';

definePageMeta({
  layout: 'empty',
});

const route = useRoute();
const router = useRouter();
const { showSnackbar } = useSnackbar();
const config = useRuntimeConfig();

const token = ref<string | null>(null);
const newPassword = ref('');
const confirmPassword = ref('');
const loading = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

onMounted(() => {
  if (typeof route.query.token === 'string') {
    token.value = route.query.token;
  } else {
    showSnackbar({ message: 'Invalid or missing password reset token.', type: 'error' });
    router.push('/login');
  }
});

const handleResetPassword = async () => {
  if (newPassword.value !== confirmPassword.value) {
    showSnackbar({ message: 'Passwords do not match.', type: 'error' });
    return;
  }
  if (!token.value) {
    showSnackbar({ message: 'No reset token found.', type: 'error' });
    return;
  }

  loading.value = true;
  try {
    await $fetch('/api/v1/auth/reset-password', {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: {
        token: token.value,
        new_password: newPassword.value,
        confirm_password: confirmPassword.value,
      },
    });
    showSnackbar({ message: 'Password has been reset successfully. Please login.', type: 'success' });
    router.push('/login');
  } catch (error: any) {
    console.error('Reset password error:', error);
    const errorMessage = error.response?._data?.detail || 'Failed to reset password. The token may be invalid or expired.';
    showSnackbar({ message: errorMessage, type: 'error' });
  } finally {
    loading.value = false;
  }
};
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
