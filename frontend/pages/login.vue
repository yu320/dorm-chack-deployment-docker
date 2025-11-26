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
              <!-- Shield Check Icon -->
              <svg xmlns="http://www.w3.org/2000/svg" class="h-10 w-10 text-white" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="1.5">
                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12.75L11.25 15 15 9.75m-3-7.036A11.959 11.959 0 013.598 6 11.99 11.99 0 003 9.749c0 5.592 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.31-.21-2.571-.598-3.751h-.152c-3.196 0-6.1-1.248-8.25-3.286zm0 13.036h.008v.008h-.008v-.008z" />
              </svg>
            </div>
          </div>
          <h1 class="text-3xl font-bold text-white">{{ $t('header.title') }}</h1>
          <p class="text-white/80 mt-2">{{ $t('login.signInPrompt') }}</p>
          <div class="text-lg font-semibold text-white/90 mt-4 clock">{{ currentTime }}</div>
        </div>
        
        <form class="space-y-6" @submit.prevent="handleLogin">
          <div>
            <label for="username" class="block text-sm font-medium text-white/90 mb-1">{{ $t('login.username') }}</label>
            <input 
              v-model="credentials.username" 
              id="username" 
              name="username"
              type="text"
              required
              class="appearance-none block w-full px-3 py-2 border border-white/30 bg-white/20 rounded-md shadow-sm placeholder-white/50 text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
            />
          </div>

          <div>
            <div class="relative">
              <input 
                v-model="credentials.password" 
                id="password" 
                name="password"
                :type="showPassword ? 'text' : 'password'"
                required
                class="appearance-none block w-full px-3 py-2 border border-white/30 bg-white/20 rounded-md shadow-sm placeholder-white/50 text-white focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm pr-10"
              />
              <button
                type="button"
                @click="showPassword = !showPassword"
                class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5 text-white/70 focus:outline-none"
              >
                <!-- Eye icon (open/closed) -->
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

          <div class="flex items-center justify-between">
            <div class="text-sm">
              <NuxtLink :to="localePath('/forgot-password')" class="font-medium text-primary-400 hover:text-primary-300">
                {{ $t('login.forgotPassword') }}
              </NuxtLink>
            </div>
            <div class="text-sm">
              <NuxtLink :to="localePath('/register')" class="font-medium text-primary-400 hover:text-primary-300">
                {{ $t('login.register') }}
              </NuxtLink>
            </div>
          </div>
          
          <div>
            <button 
              type="submit" 
              :disabled="loading"
              class="w-full flex justify-center py-3 px-4 border border-transparent rounded-lg shadow-lg text-white font-semibold bg-primary-600 hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 transition transform hover:scale-105 active:scale-95 disabled:bg-primary-400 disabled:cursor-not-allowed"
            >
              <span v-if="loading">Signing In...</span>
              <span v-else>{{ $t('login.signIn') }}</span>
            </button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted, onUnmounted } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useRouter } from 'vue-router';
import { useI18n } from '#imports';
import { useSnackbar } from '~/composables/useSnackbar';
import Snackbar from '~/components/common/Snackbar.vue';

definePageMeta({
  layout: false // Do not use the default layout for the login page
})

// --- Language Switcher Logic ---
const { locale, locales } = useI18n();
const switchLocalePath = useSwitchLocalePath();
const localePath = useLocalePath();

const langDropdownOpen = ref(false);

const currentLocale = computed(() => {
  return locales.value.find(l => l.code === locale.value);
});

const availableLocales = computed(() => {
  return locales.value.filter(l => l.code !== locale.value);
});

// --- Login & Auth Logic ---
const credentials = ref({
  username: '',
  password: ''
});
const loading = ref(false);
const showPassword = ref(false);

const { login, isAuthenticated } = useAuth();
const router = useRouter();
const { showSnackbar } = useSnackbar();
const { t } = useI18n();

const handleLogin = async () => {
  loading.value = true;
  const success = await login(credentials.value.username, credentials.value.password);
  if (success) {
    router.push(localePath('/')); // Redirect to home page on successful login
  } else {
    showSnackbar({ message: t('snackbar.loginFailed'), type: 'error' });
  }
  loading.value = false;
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
  // If already authenticated, redirect to home page
  if (isAuthenticated.value) {
    router.push(localePath('/'));
  }
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
.animate-pulse-slow {
  animation: pulse 6s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
.animate-pulse-slow-delay {
  animation: pulse 7s cubic-bezier(0.4, 0, 0.6, 1) infinite;
}
@keyframes pulse {
  0%, 100% {
    opacity: 0.5;
    transform: scale(1);
  }
  50% {
    opacity: 0.2;
    transform: scale(1.3);
  }
}
</style>