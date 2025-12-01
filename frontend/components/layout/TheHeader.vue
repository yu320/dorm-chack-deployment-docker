<script setup lang="ts">
import { ref, reactive, computed } from 'vue';
import { useRoute } from 'vue-router';
import { useI18n } from '#imports'; // Use Nuxt's auto-import for i18n
import { useAuth } from '~/composables/useAuth';
import { useTheme } from '~/composables/useTheme';
import { useSnackbar } from '~/composables/useSnackbar'; // Added useSnackbar
import { useDropdown } from '~/composables/useDropdown';
import GlobalSearchBar from '~/components/common/GlobalSearchBar.vue'; // Import GlobalSearchBar

const route = useRoute();
const { locale, locales, t } = useI18n();
const switchLocalePath = useSwitchLocalePath();
const localePath = useLocalePath();

const { isAuthenticated, user, logout, hasPermission, apiFetch } = useAuth();
const { theme, toggleTheme } = useTheme();
const { showSnackbar } = useSnackbar();

const { isOpen: isLangOpen, dropdownRef: langDropdownRef, toggleRef: langToggleRef, open: openLangDropdown, close: closeLangDropdown, toggle: toggleLangDropdown } = useDropdown();
const { isOpen: isAdminOpen, dropdownRef: adminDropdownRef, toggleRef: adminToggleRef, open: openAdminDropdown, close: closeAdminDropdown, toggle: toggleAdminDropdown } = useDropdown();
const { isOpen: isPatrolOpen, dropdownRef: patrolDropdownRef, toggleRef: patrolToggleRef, open: openPatrolDropdown, close: closePatrolDropdown, toggle: togglePatrolDropdown } = useDropdown();

// Admin Dropdowns
const { isOpen: isInspOpen, dropdownRef: inspDropdownRef, toggleRef: inspToggleRef, open: openInspDropdown, close: closeInspDropdown, toggle: toggleInspDropdown } = useDropdown();
const { isOpen: isDormOpen, dropdownRef: dormDropdownRef, toggleRef: dormToggleRef, open: openDormDropdown, close: closeDormDropdown, toggle: toggleDormDropdown } = useDropdown();
const { isOpen: isSysOpen, dropdownRef: sysDropdownRef, toggleRef: sysToggleRef, open: openSysDropdown, close: closeSysDropdown, toggle: toggleSysDropdown } = useDropdown();

// Array of all close functions for easy management
const allDropdownCloseFunctions = [
  closeLangDropdown,
  closeAdminDropdown,
  closePatrolDropdown,
  closeInspDropdown,
  closeDormDropdown,
  closeSysDropdown,
];

const closeAllDropdowns = (exceptCloseFn?: Function) => {
  allDropdownCloseFunctions.forEach(closeFn => {
    if (closeFn !== exceptCloseFn) {
      closeFn();
    }
  });
};

const mobileMenuOpen = ref(false);

let closeDropdownTimer: ReturnType<typeof setTimeout> | null = null; // Timer for dropdown closing delay

const onMouseEnter = (openFn: () => void, currentCloseFn: Function) => {
  if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) {
    if (closeDropdownTimer) {
      clearTimeout(closeDropdownTimer);
      closeDropdownTimer = null;
    }
    closeAllDropdowns(currentCloseFn); // Close others before opening this one
    openFn();
  }
};

const onMouseLeave = (closeFn: () => void) => {
  if (typeof window !== 'undefined' && window.matchMedia('(min-width: 768px)').matches) {
    if (closeDropdownTimer) {
      clearTimeout(closeDropdownTimer);
    }
    closeDropdownTimer = setTimeout(() => {
      closeFn();
      closeDropdownTimer = null;
    }, 200); // 200ms delay before closing
  }
};

const showChangePasswordModal = ref(false);
const changePasswordData = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

const showCurrentPassword = ref(false);
const showNewPassword = ref(false);
const showConfirmPassword = ref(false);

const openChangePasswordModal = () => {
  // Reset fields when opening
  changePasswordData.current_password = '';
  changePasswordData.new_password = '';
  changePasswordData.confirm_password = '';
  showChangePasswordModal.value = true;
};

const handlePasswordChange = async () => {
  if (changePasswordData.new_password !== changePasswordData.confirm_password) {
    showSnackbar({ message: t('snackbar.passwordsDoNotMatch'), type: 'error' });
    return;
  }
  try {
    await apiFetch('/api/v1/users/change-password', {
      method: 'POST',
      body: changePasswordData,
    });
    showSnackbar({ message: t('snackbar.passwordChangedSuccessfully'), type: 'success' });
    showChangePasswordModal.value = false;
  } catch (error: any) {
    const errorMessage = error.data?.detail || t('snackbar.failedToChangePassword');
    showSnackbar({ message: errorMessage, type: 'error' });
  }
};

const isAdmin = computed(() => {
  return isAuthenticated.value && hasPermission('admin:full_access');
});

const isStudent = computed(() => {
  return isAuthenticated.value && !hasPermission('admin:full_access');
});

const currentLocale = computed(() => {
  return locales.value.find(l => l.code === locale.value);
});

const availableLocales = computed(() => {
  return locales.value.filter(l => l.code !== locale.value);
});

const handleLogout = async () => {
  await logout();
  await navigateTo(localePath('/login'));
};

</script>
<template>
  <div>
    <header class="bg-white dark:bg-gray-800 shadow-lg">
      <div class="container mx-auto px-4 py-5 flex flex-wrap justify-between items-center gap-4">
        <NuxtLink :to="localePath('/')" class="flex items-center cursor-pointer">
          <!-- Placeholder for logo -->
          <div class="h-12 w-12 rounded-full shadow-md mr-4 bg-primary-200 dark:bg-primary-800"></div>
          <div>
            <h1 class="text-3xl md:text-4xl font-extrabold text-primary-800 dark:text-primary-200">{{ $t('header.title') }}</h1>
            <p class="text-gray-500 dark:text-gray-400 text-sm md:text-base mt-1">{{ $t('header.subtitle') }}</p>
          </div>
        </NuxtLink>

        <div class="flex-grow max-w-sm mx-auto sm:max-w-xs md:max-w-md lg:max-w-lg">
          <GlobalSearchBar v-if="isAuthenticated" />
        </div>

        <div class="flex flex-col sm:flex-row items-center sm:justify-end gap-4 w-full sm:w-auto">
          <div class="flex items-center justify-between gap-3 flex-nowrap"> <!-- New wrapper for Menu, Language, Dark Mode -->
            <!-- Hamburger Menu Button for Mobile -->
            <button @click="mobileMenuOpen = !mobileMenuOpen" class="sm:hidden p-2 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200 min-w-0 flex-shrink-0">
              <svg v-if="!mobileMenuOpen" xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h16" />
              </svg>
              <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>

            <div class="flex items-center gap-3">
              <!-- Language Switcher -->
              <div class="relative min-w-0" @mouseenter="onMouseEnter(openLangDropdown, closeLangDropdown)" @mouseleave="onMouseLeave(closeLangDropdown)">
                <button ref="langToggleRef" @click="toggleLangDropdown(); closeAllDropdowns(closeLangDropdown);" class="p-2 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center">
                  <Icon name="heroicons:language" class="h-5 w-5" />
                  <span class="ml-2 text-sm font-medium hidden sm:inline">{{ currentLocale?.name }}</span>
                  <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isLangOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
                <div ref="langDropdownRef" v-if="isLangOpen" class="dropdown-menu-floating" :class="{'dropdown-active': isLangOpen}">
                  <NuxtLink v-for="l in availableLocales" :key="l.code" :to="switchLocalePath(l.code)" @click="closeLangDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                    {{ l.name }}
                  </NuxtLink>
                </div>
              </div>

              <!-- Dark Mode Toggle -->
              <button @click="toggleTheme" class="flex-shrink-0 p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 min-w-0">
                <!-- Sun Icon (Show when in Dark Mode to switch to Light) -->
                <svg v-if="theme === 'dark'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path d="M12 2.25a.75.75 0 01.75.75v2.25a.75.75 0 01-1.5 0V3a.75.75 0 01.75-.75zM7.5 12a4.5 4.5 0 119 0 4.5 4.5 0 01-9 0zM18.894 6.166a.75.75 0 00-1.06-1.06l-1.591 1.59a.75.75 0 101.06 1.061l1.591-1.59zM21.75 12a.75.75 0 01-.75.75h-2.25a.75.75 0 010-1.5H21a.75.75 0 01.75.75zM17.834 18.894a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 10-1.061 1.06l1.59 1.591zM12 18a.75.75 0 01.75.75V21a.75.75 0 01-1.5 0v-2.25A.75.75 0 0112 18zM7.758 17.303a.75.75 0 00-1.061-1.06l-1.591 1.59a.75.75 0 001.06 1.061l1.591-1.59zM6 12a.75.75 0 01-.75.75H3a.75.75 0 010-1.5h2.25A.75.75 0 016 12zM6.697 7.757a.75.75 0 001.06-1.06l-1.59-1.591a.75.75 0 00-1.061 1.06l1.59 1.591z" />
                </svg>
                <!-- Moon Icon (Show when in Light Mode to switch to Dark) -->
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 24 24" fill="currentColor">
                  <path fill-rule="evenodd" d="M9.528 1.718a.75.75 0 01.162.819A8.97 8.97 0 009 6a9 9 0 009 9 8.97 8.97 0 003.463-.69.75.75 0 01.981.98 10.503 10.503 0 01-9.694 6.46c-5.799 0-10.5-4.701-10.5-10.5 0-4.368 2.667-8.112 6.46-9.694a.75.75 0 01.818.162z" clip-rule="evenodd" />
                </svg>
              </button>
            </div>
          </div>

          <template v-if="isAuthenticated">
            <div class="w-full sm:w-auto">
              <span class="sm:w-auto text-gray-700 dark:text-gray-300 font-medium px-3 py-1 bg-gray-100 dark:bg-gray-700 rounded-full order-first sm:order-none">
                {{ $t('header.welcome') }}, {{ user?.student?.full_name || user?.username }}<template v-if="user?.student"> ({{ user.student.student_id_number }})</template>
              </span>
            </div>
            <div class="w-full sm:w-auto">
              <button @click="openChangePasswordModal" class="w-full bg-yellow-500 hover:bg-yellow-600 text-white font-medium py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 shadow-sm flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" viewBox="0 0 24 24" fill="currentColor">
                  <path fill-rule="evenodd" d="M12 1.5a5.25 5.25 0 00-5.25 5.25v3a3 3 0 00-3 3v6.75a3 3 0 003 3h10.5a3 3 0 003-3v-6.75a3 3 0 00-3-3v-3c0-2.9-2.35-5.25-5.25-5.25zm3.75 8.25v-3a3.75 3.75 0 10-7.5 0v3h7.5z" clip-rule="evenodd" />
                </svg>
                {{ $t('header.changePassword') }}
              </button>
            </div>
            <div class="w-full sm:w-auto">
              <button @click="handleLogout" class="w-full bg-red-500 hover:bg-red-600 text-white font-medium py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 shadow-sm flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" /></svg>
                {{ $t('header.logout') }}
              </button>
            </div>
          </template>
          <template v-else>
            <div class="w-full sm:w-auto">
              <NuxtLink :to="localePath('/login')" class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition duration-300 transform hover:scale-105 shadow-sm flex items-center justify-center">
                {{ $t('login.signIn') }}
              </NuxtLink>
            </div>
          </template>
        </div>
      </div>
    </header>
    <div v-if="isAuthenticated" class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-40">
      <div class="container mx-auto px-4">
        <div class="flex flex-nowrap overflow-x-auto md:overflow-visible border-b border-gray-200 dark:border-gray-700 w-full scrollbar-hide" :class="{'!flex !flex-col !overflow-visible !whitespace-normal': mobileMenuOpen}">
          <NuxtLink :to="localePath('/')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.home') }}</NuxtLink>
          
          <!-- Admin Navigation -->
          <template v-if="isAdmin">
            <!-- Dashboard -->
            <NuxtLink :to="localePath('/admin/dashboard')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.dashboard') }}</NuxtLink>
            
            <!-- Inspection Management -->
            <div class="relative" @mouseenter="onMouseEnter(openInspDropdown, closeInspDropdown)" @mouseleave="onMouseLeave(closeInspDropdown)">
              <button ref="inspToggleRef" @click="toggleInspDropdown(); closeAllDropdowns(closeInspDropdown);" class="tab-button flex items-center">
                <span>{{ $t('admin.manageInspections') }}</span>
                <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isInspOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              <div ref="inspDropdownRef" v-if="isInspOpen" class="dropdown-menu-floating" :class="{'dropdown-active': isInspOpen}">
                <NuxtLink :to="localePath('/admin/inspections')" @click="closeInspDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.inspections') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/new-inspection')" @click="closeInspDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.newAdminInspection') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/items')" @click="closeInspDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.items') }}</NuxtLink>
              </div>
            </div>

            <!-- Dorm Management -->
            <div class="relative" @mouseenter="onMouseEnter(openDormDropdown, closeDormDropdown)" @mouseleave="onMouseLeave(closeDormDropdown)">
              <button ref="dormToggleRef" @click="toggleDormDropdown(); closeAllDropdowns(closeDormDropdown);" class="tab-button flex items-center">
                <span>{{ $t('admin.manageDorms') || 'Dorm Management' }}</span>
                <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isDormOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              <div ref="dormDropdownRef" v-if="isDormOpen" class="dropdown-menu-floating" :class="{'dropdown-active': isDormOpen}">
                <NuxtLink :to="localePath('/admin/students')" @click="closeDormDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.students') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/rooms')" @click="closeDormDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.rooms') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/rooms-students')" @click="closeDormDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.roomsStudents') }}</NuxtLink>
              </div>
            </div>

            <!-- System Settings -->
            <div class="relative" @mouseenter="onMouseEnter(openSysDropdown, closeSysDropdown)" @mouseleave="onMouseLeave(closeSysDropdown)">
              <button ref="sysToggleRef" @click="toggleSysDropdown(); closeAllDropdowns(closeSysDropdown);" class="tab-button flex items-center">
                <span>{{ $t('admin.systemSettings') || 'System' }}</span>
                <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isSysOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              <div ref="sysDropdownRef" v-if="isSysOpen" class="dropdown-menu-floating right-0" :class="{'dropdown-active': isSysOpen}">
                <NuxtLink :to="localePath('/admin/announcements')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('admin.announcementsTitle') || 'Announcements' }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/users')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.users') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/settings')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.settings') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/advanced-search')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.advancedSearch') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/pdf-reports')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.pdfReports') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/email-notifications')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.emailNotifications') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/data-backup')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.dataBackup') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/data-import')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.dataImport') }}</NuxtLink>
                <NuxtLink :to="localePath('/admin/audit-logs')" @click="closeSysDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('admin.auditLogsTitle') }}</NuxtLink>
              </div>
            </div>
          </template>

          <!-- Student Navigation (Visible to all authenticated users) -->
          <template v-if="isAuthenticated">
            <NuxtLink :to="localePath('/inspection/new')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.newInspection') }}</NuxtLink>
            <NuxtLink :to="localePath('/records')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.myRecords') }}</NuxtLink>
          </template>

          <!-- Patrol Navigation -->
          <div v-if="isAuthenticated" class="relative" @mouseenter="onMouseEnter(openPatrolDropdown, closePatrolDropdown)" @mouseleave="onMouseLeave(closePatrolDropdown)">
            <button ref="patrolToggleRef" @click="togglePatrolDropdown(); closeAllDropdowns(closePatrolDropdown);" class="tab-button flex items-center" :class="{ 'tab-active': $route.path.startsWith('/patrol') }">
              <span>{{ $t('navigation.patrol') }}</span>
              <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isPatrolOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
            </button>
            <div ref="patrolDropdownRef" v-if="isPatrolOpen" class="dropdown-menu-floating right-0" :class="{'dropdown-active': isPatrolOpen}">
              <NuxtLink v-if="hasPermission('manage_patrol_locations')" :to="localePath('/patrol/locations')" @click="closePatrolDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.patrolLocations') }}</NuxtLink>
              <NuxtLink v-if="hasPermission('lights_out_check_perform')" :to="localePath('/patrol/inspect')" @click="closePatrolDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.performInspection') }}</NuxtLink>
              <NuxtLink v-if="hasPermission('lights_out_check_perform')" :to="localePath('/patrol/history')" @click="closePatrolDropdown(); mobileMenuOpen = false;" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">{{ $t('navigation.inspectionHistory') }}</NuxtLink>
            </div>
          </div>
        </div>
      </div>
    </div>
    <!-- Change Password Modal -->
    <div v-if="showChangePasswordModal" class="fixed inset-0 bg-gray-600 bg-opacity-75 overflow-y-auto h-full w-full z-50 flex justify-center items-center">
      <div class="relative p-6 bg-white dark:bg-gray-800 w-full max-w-md mx-auto rounded-lg shadow-xl">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">{{ $t('header.changePassword') }}</h3>
        <form @submit.prevent="handlePasswordChange">
          <div class="space-y-4">
            <div>
              <label for="current_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('login.password') }}</label>
              <div class="relative">
                <input type="password" v-model="changePasswordData.current_password" id="current_password" :type="showCurrentPassword ? 'text' : 'password'" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm pr-10" required>
                <button
                  type="button"
                  @click="showCurrentPassword = !showCurrentPassword"
                  class="absolute inset-y-0 right-0 pr-3 flex items-center text-sm leading-5 text-gray-700 dark:text-gray-300 focus:outline-none"
                >
                                  <svg v-if="!showCurrentPassword" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.036 12.322a1.012 1.012 0 010-.639C3.423 7.51 7.36 4.5 12 4.5c4.638 0 8.573 3.007 9.963 7.178.07.207.07.431 0 .639C20.577 16.49 16.64 19.5 12 19.5c-4.638 0-8.573-3.007-9.963-7.178z" />
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                                  </svg>
                                  <svg v-else xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="w-5 h-5">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M3.98 8.223A10.477 10.477 0 001.934 12C3.226 16.338 7.244 19.5 12 19.5c.993 0 1.953-.138 2.863-.395M6.228 6.228A10.45 10.45 0 0112 4.5c4.756 0 8.773 3.162 10.065 7.498a10.523 10.523 0 01-4.293 5.774M6.228 6.228L3 3m3.228 3.228l3.65 3.65m7.894 7.894L21 21m-3.228-3.228l-3.65-3.65m0 0a3 3 0 10-4.243-4.243m4.242 4.242L9.88 9.88" />
                                  </svg>                </button>
              </div>
            </div>
            <div>
              <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('login.newPassword') }}</label>
              <div class="relative">
                <input type="password" v-model="changePasswordData.new_password" id="new_password" :type="showNewPassword ? 'text' : 'password'" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm pr-10" required>
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
                                  </svg>                </button>
              </div>
            </div>
            <div>
              <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('login.confirmPassword') }}</label>
              <div class="relative">
                <input type="password" v-model="changePasswordData.confirm_password" id="confirm_password" :type="showConfirmPassword ? 'text' : 'password'" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm pr-10" required>
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
                                  </svg>                </button>
              </div>
            </div>
          </div>
          <div class="flex justify-end space-x-4 mt-6">
            <button type="button" @click="showChangePasswordModal = false" class="px-4 py-2 text-sm font-medium text-gray-700 bg-gray-200 rounded-md">{{ $t('admin.cancel') }}</button>
            <button type="submit" class="px-4 py-2 text-sm font-medium text-white bg-primary-600 rounded-md">{{ $t('admin.save') }}</button>
          </div>
        </form>
      </div>
    </div>
  </div>
</template>
