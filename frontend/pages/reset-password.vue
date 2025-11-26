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
          <input
            id="new_password"
            name="new_password"
            type="password"
            required
            v-model="newPassword"
            class="block w-full px-4 py-3 mt-1 border-gray-300 rounded-lg shadow-sm bg-white/80 dark:bg-gray-700/80 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
        </div>
        <div>
          <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">Confirm New Password</label>
          <input
            id="confirm_password"
            name="confirm_password"
            type="password"
            required
            v-model="confirmPassword"
            class="block w-full px-4 py-3 mt-1 border-gray-300 rounded-lg shadow-sm bg-white/80 dark:bg-gray-700/80 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-primary-500"
          />
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
