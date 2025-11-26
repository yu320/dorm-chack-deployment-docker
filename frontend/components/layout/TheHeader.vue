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

const { isOpen: isLangOpen, dropdownRef: langDropdownRef, toggleRef: langToggleRef, toggle: toggleLangDropdown, close: closeLangDropdown } = useDropdown();

// Admin Dropdowns
const { isOpen: isInspOpen, dropdownRef: inspDropdownRef, toggleRef: inspToggleRef, toggle: toggleInspDropdown, close: closeInspDropdown } = useDropdown();
const { isOpen: isDormOpen, dropdownRef: dormDropdownRef, toggleRef: dormToggleRef, toggle: toggleDormDropdown, close: closeDormDropdown } = useDropdown();
const { isOpen: isSysOpen, dropdownRef: sysDropdownRef, toggleRef: sysToggleRef, toggle: toggleSysDropdown, close: closeSysDropdown } = useDropdown();


const mobileMenuOpen = ref(false);

const showChangePasswordModal = ref(false);
const changePasswordData = reactive({
  current_password: '',
  new_password: '',
  confirm_password: '',
});

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
              <div class="relative min-w-0">
                <button ref="langToggleRef" @click="toggleLangDropdown" class="p-2 rounded-md bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors duration-200 flex items-center">
                  <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke-width="1.5" stroke="currentColor" class="h-5 w-5">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M10.5 21l5.25-11.25L21 21m-9-6h5.25M7.5 8.25V5.25m0 0h3.75m-3.75 0l-1.5-1.5M7.5 5.25v3.75m4.5-4.5v4.5m-4.5-4.5h4.5m-4.5 0l-1.5-1.5M12 12.75l-3-3m3 3l3-3m-3 3v3.75m-9-6h5.25M7.5 8.25V5.25m0 0h3.75m-3.75 0l-1.5-1.5M7.5 5.25v3.75m4.5-4.5v4.5m-4.5-4.5h4.5m-4.5 0l-1.5-1.5M12 12.75l-3-3m3 3l3-3m-3 3v3.75" />
                  </svg>
                  <span class="ml-2 text-sm font-medium hidden sm:inline">{{ currentLocale?.name }}</span>
                  <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isLangOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
                </button>
                <div ref="langDropdownRef" v-if="isLangOpen" class="dropdown-menu-floating" :class="{'dropdown-active': isLangOpen}">
                  <NuxtLink v-for="l in availableLocales" :key="l.code" :to="switchLocalePath(l.code)" @click="closeLangDropdown" class="block px-4 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700">
                    {{ l.name }}
                  </NuxtLink>
                </div>
              </div>

              <!-- Dark Mode Toggle -->
              <button @click="toggleTheme" class="flex-shrink-0 p-2 rounded-full bg-gray-200 dark:bg-gray-700 text-gray-800 dark:text-gray-200 hover:bg-gray-300 dark:hover:bg-gray-600 transition-colors duration-200 min-w-0">
                <svg v-if="theme === 'light'" xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M17.293 13.293A8 8 0 016.707 2.707a8.001 8.001 0 1010.586 10.586z" />
                </svg>
                <svg v-else xmlns="http://www.w3.org/2000/svg" class="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path fill-rule="evenodd" d="M10 2a1 1 0 011 1v1a1 1 0 11-2 0V3a1 1 0 011-1zm4 4a1 1 0 011 1v1a1 1 0 11-2 0V7a1 1 0 011-1zM3 10a1 1 0 011-1h1a1 1 0 110 2H4a1 1 0 01-1-1zm14 0a1 1 0 011-1h1a1 1 0 110 2h-1a1 1 0 01-1-1zm-9 9a1 1 0 011-1v1a1 1 0 11-2 0v-1a1 1 0 011-1zm-4-4a1 1 0 011-1h1a1 1 0 110 2H7a1 1 0 01-1-1zm10 0a1 1 0 011-1h1a1 1 0 110 2h-1a1 1 0 01-1-1zM6 10a4 4 0 118 0 4 4 0 01-8 0z" clip-rule="evenodd" />
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
                <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 7a2 2 0 012 2m4 0a6 6 0 01-7.743 5.743L11 17H9v2H7v2H5v-2H3v-2H1v-4a1 1 0 011-1h2V7a1 1 0 011-1h2V5a1 1 0 011-1h2V3a1 1 0 011-1h2V1a1 1 0 011-1h2V-1" /></svg>
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
    <div class="bg-white dark:bg-gray-800 shadow-sm sticky top-0 z-40">
      <div class="container mx-auto px-4">
        <div class="flex flex-wrap border-b border-gray-200 dark:border-gray-700 w-full" :class="{'!flex !flex-col': mobileMenuOpen}">
          <NuxtLink :to="localePath('/')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.home') }}</NuxtLink>
          
          <!-- Admin Navigation -->
          <template v-if="isAdmin">
            <!-- Dashboard -->
            <NuxtLink :to="localePath('/admin/dashboard')" @click="mobileMenuOpen = false" class="tab-button" active-class="tab-active">{{ $t('navigation.dashboard') }}</NuxtLink>
            
            <!-- Inspection Management -->
            <div class="relative">
              <button ref="inspToggleRef" @click="toggleInspDropdown" class="tab-button flex items-center">
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
            <div class="relative">
              <button ref="dormToggleRef" @click="toggleDormDropdown" class="tab-button flex items-center">
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
            <div class="relative">
              <button ref="sysToggleRef" @click="toggleSysDropdown" class="tab-button flex items-center">
                <span>{{ $t('admin.systemSettings') || 'System' }}</span>
                <svg class="w-4 h-4 ml-1 transition-transform" :class="{'rotate-180': isSysOpen}" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7"></path></svg>
              </button>
              <div ref="sysDropdownRef" v-if="isSysOpen" class="dropdown-menu-floating right-0" :class="{'dropdown-active': isSysOpen}">
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

          <template v-if="isAuthenticated">
          </template>
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
              <input type="password" v-model="changePasswordData.current_password" id="current_password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="new_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('login.newPassword') }}</label>
              <input type="password" v-model="changePasswordData.new_password" id="new_password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
            </div>
            <div>
              <label for="confirm_password" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('login.confirmPassword') }}</label>
              <input type="password" v-model="changePasswordData.confirm_password" id="confirm_password" class="mt-1 block w-full border-gray-300 rounded-md shadow-sm" required>
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
