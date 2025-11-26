<template>
  <div class="relative min-h-screen flex items-center justify-center p-4 overflow-hidden">
    <Snackbar />
    <div class="image-background"></div>
    <!-- Language Switcher -->
    <div class="absolute top-4 right-4 z-20">
      <div class="relative">
        <button @click="langDropdownOpen = !langDropdownOpen" class="p-2 rounded-md bg-white/10 backdrop-blur-sm text-white hover:bg-white/20 transition-colors duration-200 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor"><path d="M10 2a8 8 0 100 16 8 8 0 000-16zM2 10a8 8 0 1116 0 8 8 0 01-16 0z" /><path d="M12.395 7.553a1 1 0 00-1.45-.385l-2.5 1.5a1 1 0 000 1.664l2.5 1.5a1 1 0 001.45-.385V7.553z" /></svg>
          <span class="ml-2 text-sm font-medium">{{ currentLocale?.name }}</span>
          <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': langDropdownOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
        </button>
        <div v-if="langDropdownOpen" class="absolute top-full right-0 mt-2 w-40 bg-white/10 backdrop-blur-lg rounded-lg shadow-xl border border-white/20 py-1">
          <NuxtLink v-for="l in availableLocales" :key="l.code" :to="switchLocalePath(l.code)" @click="langDropdownOpen = false" class="block px-4 py-2 text-sm text-white hover:bg-white/20">
            {{ l.name }}
          </NuxtLink>
        </div>
      </div>
    </div>

    <div class="relative z-10 w-full max-w-md">
      <div class="bg-white/10 dark:bg-black/20 backdrop-blur-lg rounded-2xl shadow-2xl border border-white/20 p-8 text-white">
        <div class="text-center mb-8">
          <div class="flex justify-center mb-4">
            <div class="bg-white/20 dark:bg-black/30 p-3 rounded-full">
              <!-- Key Icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M15.75 5.25a3 3 0 013 3m3 0a6 6 0 01-7.029 5.912c-.563-.097-1.159.026-1.563.43L10.5 17.25H8.25v2.25H6v2.25H2.25v-2.818c0-.597.237-1.17.659-1.591l6.499-6.499c.404-.404.527-1 .43-1.563A6 6 0 1121.75 8.25z" />
              </svg>
            </div>
          </div>
          <h1 class="text-3xl font-bold text-white">{{ t('forgotPassword.title') }}</h1>
          <p class="text-white/80 mt-2">{{ t('forgotPassword.description') }}</p>
          <div class="text-lg font-semibold text-white/90 mt-4 clock">{{ currentTime }}</div>
        </div>

        <form @submit.prevent="handleForgotPassword" class="space-y-6">
          <div>
            <label for="email" class="block text-sm font-medium text-white/90 mb-1">{{ t('forgotPassword.email') }}</label>
            <input
              id="email"
              name="email"
              type="email"
              autocomplete="email"
              required
              v-model="email"
              class="w-full pl-4 pr-4 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
            />
          </div>

          <div>
            <button
              type="submit"
              :disabled="loading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-white font-semibold bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition transform hover:scale-105 active:scale-95 disabled:bg-primary-400 disabled:cursor-not-allowed"
            >
              <span v-if="loading">{{ t('forgotPassword.submitting') }}</span>
              <span v-else>{{ t('forgotPassword.submit') }}</span>
            </button>
          </div>
        </form>
        <div class="text-sm text-center mt-6">
          <NuxtLink :to="localePath('/login')" class="font-medium text-primary-400 hover:text-primary-300 transition-colors duration-200">
            {{ t('forgotPassword.backToLogin') }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useSnackbar } from '~/composables/useSnackbar';
import { useI18n } from '#imports';
import Snackbar from '~/components/common/Snackbar.vue';

definePageMeta({
  layout: false,
});

// --- Language Switcher Logic ---
const { locale, locales, t } = useI18n();
const switchLocalePath = useSwitchLocalePath();
const localePath = useLocalePath();

const langDropdownOpen = ref(false);

const currentLocale = computed(() => {
  return locales.value.find(l => l.code === locale.value);
});

const availableLocales = computed(() => {
  return locales.value.filter(l => l.code !== locale.value);
});

// --- Forgot Password Logic ---
const email = ref('');
const loading = ref(false);
const { showSnackbar } = useSnackbar();
const config = useRuntimeConfig();

const handleForgotPassword = async () => {
  loading.value = true;
  try {
    await $fetch('/api/v1/auth/password-recovery', {
      baseURL: config.public.apiBase,
      method: 'POST',
      body: { email: email.value },
    });
    // The backend will always return a positive message for security reasons
    showSnackbar({ message: t('forgotPassword.success'), type: 'success' });
  } catch (error: any) {
    console.error('Forgot password error:', error);
    // Show a generic message even on error for security
    showSnackbar({ message: t('forgotPassword.success'), type: 'success' });
  } finally {
    loading.value = false;
  }
};

// --- Clock Logic ---
const currentTime = ref('');
let clockInterval: any = null;

const updateClock = () => {
  const now = new Date();
  const hours = String(now.getHours()).padStart(2, '0');
  const minutes = String(now.getMinutes()).padStart(2, '0');
  const seconds = String(now.getSeconds()).padStart(2, '0');
  currentTime.value = `${hours}:${minutes}:${seconds}`;
};

onMounted(() => {
  updateClock();
  clockInterval = setInterval(updateClock, 1000);
});

onUnmounted(() => {
  clearInterval(clockInterval);
});
</script>

<style scoped>
.image-background {
  background-image: url('/login.jpg');
  background-size: cover;
  background-position: center;
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  filter: blur(4px) brightness(0.7);
  transform: scale(1.05);
}
.clock {
  font-family: 'Courier New', Courier, monospace;
}
</style>
