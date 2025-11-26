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
              <!-- User Plus Icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M19 7.5v3m0 0v3m0-3h3m-3 0h-3m-2.25-4.125a3.375 3.375 0 11-6.75 0 3.375 3.375 0 016.75 0zM4 19.235v-.11a6.375 6.375 0 0112.75 0v.109A12.318 12.318 0 0110.374 21c-2.331 0-4.512-.645-6.374-1.766z" />
              </svg>
            </div>
          </div>
          <h1 class="text-3xl font-bold text-white">{{ t('register.title') }}</h1>
          <div class="text-lg font-semibold text-white/90 mt-4 clock">{{ currentTime }}</div>
        </div>

        <form @submit.prevent="handleRegister" class="space-y-6">
          <div>
            <label for="username" class="block text-sm font-medium text-white/90 mb-1">{{ t('register.username') }}</label>
            <input
              id="username"
              name="username"
              type="text"
              autocomplete="username"
              required
              v-model="username"
              class="w-full pl-4 pr-4 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
            />
          </div>
          <div>
            <label for="bed_number" class="block text-sm font-medium text-white/90 mb-1">{{ t('register.bedNumber') }}</label>
            <input
              id="bed_number"
              name="bed_number"
              type="text"
              required
              v-model="bedNumber"
              class="w-full pl-4 pr-4 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
            />
          </div>
          <div>
            <label for="student_id_number" class="block text-sm font-medium text-white/90 mb-1">{{ t('register.studentId') }}</label>
            <input
              id="student_id_number"
              name="student_id_number"
              type="text"
              required
              v-model="studentIdNumber"
              class="w-full pl-4 pr-4 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
            />
          </div>
          <div class="text-sm text-white/80">
            {{ t('register.emailNote') }} <span class="font-medium text-primary-300">{{ generatedEmail }}</span>
          </div>
          <div>
            <label for="password" class="block text-sm font-medium text-white/90 mb-1">{{ t('register.password') }}</label>
            <div class="relative">
              <input
                id="password"
                name="password"
                :type="showPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                v-model="password"
                class="w-full pl-4 pr-12 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
              />
              <button 
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-white/70 hover:text-white transition-colors focus:outline-none"
              >
                <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
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
            <label for="confirm_password" class="block text-sm font-medium text-white/90 mb-1">{{ t('register.confirmPassword') }}</label>
            <div class="relative">
              <input
                id="confirm_password"
                name="confirm_password"
                :type="showConfirmPassword ? 'text' : 'password'"
                autocomplete="new-password"
                required
                v-model="confirmPassword"
                class="w-full pl-4 pr-12 py-3 bg-white/10 dark:bg-black/20 border border-white/20 rounded-lg placeholder-white/50 focus:bg-white/20 dark:focus:bg-black/30 focus:ring-2 focus:ring-primary-400 focus:outline-none transition text-white"
              />
              <button 
                type="button"
                @click="showConfirmPassword = !showConfirmPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-white/70 hover:text-white transition-colors focus:outline-none"
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
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-white font-semibold bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition transform hover:scale-105 active:scale-95 disabled:bg-primary-400 disabled:cursor-not-allowed"
            >
              <span v-if="loading">{{ t('register.submitting') }}</span>
              <span v-else>{{ t('register.submit') }}</span>
            </button>
          </div>
        </form>
        <div class="text-sm text-center mt-6">
          <NuxtLink :to="localePath('/login')" class="font-medium text-primary-400 hover:text-primary-300 transition-colors duration-200">
            {{ t('register.hasAccount') }} {{ t('register.login') }}
          </NuxtLink>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { useRouter } from 'vue-router';
import { useAuth } from '~/composables/useAuth';
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

// --- Register Logic ---
const username = ref('');
const bedNumber = ref('');
const studentIdNumber = ref('');
const password = ref('');
const confirmPassword = ref('');
const showPassword = ref(false);
const showConfirmPassword = ref(false);
const loading = ref(false);
const emailDomain = '@gmail.com'; // Configurable domain

const router = useRouter();
const { register } = useAuth();
const { showSnackbar } = useSnackbar();

const generatedEmail = computed(() => {
  if (studentIdNumber.value) {
    return `${studentIdNumber.value}${emailDomain}`;
  }
  return `...${emailDomain}`;
});

const handleRegister = async () => {
  if (password.value !== confirmPassword.value) {
    showSnackbar({ message: t('register.passwordsDoNotMatch'), type: 'error' });
    return;
  }
  if (!studentIdNumber.value) {
    showSnackbar({ message: t('register.missingStudentId'), type: 'error' });
    return;
  }

  loading.value = true;
  try {
    await register(username.value, password.value, studentIdNumber.value, generatedEmail.value, bedNumber.value);
    showSnackbar({ message: t('register.success'), type: 'success' });
    router.push(localePath('/login'));
  } catch (error: any) {
    console.error('Registration failed:', error);
    const errorMessage = error.response?._data?.detail || 'Registration failed.';
    showSnackbar({ message: errorMessage, type: 'error' });
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