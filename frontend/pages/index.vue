<template>
  <div class="container mx-auto px-4 py-8">
    <div v-if="!isAuthenticated" class="py-20 text-center">
      <!-- Logged-out view: Hero Section -->
      <div class="max-w-3xl mx-auto">
        <h1 class="text-5xl md:text-6xl font-extrabold text-gray-800 dark:text-white mb-6 leading-tight">
          {{ $t('welcome') }}
        </h1>
        <p class="mt-4 text-xl text-gray-600 dark:text-gray-300 mb-10">
          {{ $t('welcomeMessage') }}
        </p>
        <NuxtLink :to="localePath('/login')" class="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-full text-white bg-primary-600 hover:bg-primary-700 md:py-4 md:text-xl md:px-10 transition-all transform hover:scale-105 shadow-lg hover:shadow-xl">
          {{ $t('getStarted') }}
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 ml-2" viewBox="0 0 20 20" fill="currentColor">
            <path fill-rule="evenodd" d="M10.293 3.293a1 1 0 011.414 0l6 6a1 1 0 010 1.414l-6 6a1 1 0 01-1.414-1.414L14.586 11H3a1 1 0 110-2h11.586l-4.293-4.293a1 1 0 010-1.414z" clip-rule="evenodd" />
          </svg>
        </NuxtLink>
      </div>
    </div>

    <div v-else-if="isStudent" class="space-y-8">
      <!-- Student-specific dashboard -->
      <div class="flex items-center justify-between">
        <h2 class="text-3xl font-bold text-gray-800 dark:text-white flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8 mr-3 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2V6zM14 6a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2V6zM4 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2H6a2 2 0 01-2-2v-2zM14 16a2 2 0 012-2h2a2 2 0 012 2v2a2 2 0 01-2 2h-2a2 2 0 01-2-2v-2z" />
          </svg>
          {{ $t('index.myDashboard.title') }}
        </h2>
      </div>

      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
        <!-- My Bed Information -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-blue-500 to-blue-600 p-4">
            <h3 class="text-lg font-semibold text-white flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6" />
              </svg>
              {{ $t('index.myBed.title') }}
            </h3>
          </div>
          <div class="p-6">
            <div v-if="user.student && user.student.bed" class="space-y-4">
              <div class="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-2">
                <span class="text-gray-500 dark:text-gray-400">{{ $t('index.myBed.building') }}</span>
                <span class="font-medium text-gray-800 dark:text-white">{{ user.student.bed.room.building.name }}</span>
              </div>
              <div class="flex justify-between items-center border-b border-gray-100 dark:border-gray-700 pb-2">
                <span class="text-gray-500 dark:text-gray-400">{{ $t('index.myBed.room') }}</span>
                <span class="font-medium text-gray-800 dark:text-white">{{ user.student.bed.room.room_number }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-500 dark:text-gray-400">{{ $t('index.myBed.bed') }}</span>
                <span class="font-medium text-gray-800 dark:text-white">{{ user.student.bed.bed_number }}</span>
              </div>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 12H4" />
              </svg>
              {{ $t('index.myBed.noBedAssigned') }}
            </div>
          </div>
        </div>

        <!-- Latest Inspection -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-green-500 to-green-600 p-4">
            <h3 class="text-lg font-semibold text-white flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
              </svg>
              {{ $t('index.latestInspection.title') }}
            </h3>
          </div>
          <div class="p-6">
            <div v-if="latestInspection" class="space-y-4">
              <div class="flex justify-between items-center">
                <span class="text-gray-500 dark:text-gray-400">{{ $t('index.latestInspection.date') }}</span>
                <span class="font-medium text-gray-800 dark:text-white">{{ new Date(latestInspection.created_at).toLocaleDateString() }}</span>
              </div>
              <div class="flex justify-between items-center">
                <span class="text-gray-500 dark:text-gray-400">{{ $t('index.latestInspection.status') }}</span>
                <span :class="`px-3 py-1 text-xs font-bold rounded-full uppercase tracking-wide ${getStatusColor(latestInspection.status)}`">
                  {{ $t(`inspection.status.${latestInspection.status}`) }}
                </span>
              </div>
              <NuxtLink :to="localePath(`/records/${latestInspection.id}`)" class="mt-4 block w-full text-center bg-green-50 dark:bg-green-900/20 text-green-600 dark:text-green-400 hover:bg-green-100 dark:hover:bg-green-900/40 font-semibold py-2 rounded-lg transition-colors">
                {{ $t('records.viewDetails') }}
              </NuxtLink>
            </div>
            <div v-else class="text-center py-8 text-gray-500">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-12 w-12 mx-auto text-gray-300 mb-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
              </svg>
              {{ $t('index.latestInspection.noRecord') }}
            </div>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-lg border border-gray-100 dark:border-gray-700 overflow-hidden hover:shadow-xl transition-shadow duration-300">
          <div class="bg-gradient-to-r from-purple-500 to-purple-600 p-4">
            <h3 class="text-lg font-semibold text-white flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
              {{ $t('index.quickActions.title') }}
            </h3>
          </div>
          <div class="p-6 flex flex-col space-y-4">
            <NuxtLink :to="localePath('/inspection/new')" class="group w-full flex items-center justify-center bg-primary-600 hover:bg-primary-700 text-white font-bold py-3 px-4 rounded-xl transition-all transform hover:scale-105 shadow-md hover:shadow-lg">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2 group-hover:animate-pulse" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4v16m8-8H4" />
              </svg>
              {{ $t('index.quickActions.newInspection') }}
            </NuxtLink>
             <NuxtLink :to="localePath('/records')" class="w-full flex items-center justify-center bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-800 dark:text-white font-bold py-3 px-4 rounded-xl transition-all transform hover:scale-105">
              <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
              </svg>
              {{ $t('records.myRecordsTitle') }}
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>

    <div v-else class="space-y-8">
      <!-- Admin Dashboard -->
      <div class="flex items-center justify-between">
        <div>
          <h1 class="text-3xl font-bold text-gray-800 dark:text-white">{{ $t('dashboard.adminTitle') }}</h1>
          <p class="text-gray-500 dark:text-gray-400 mt-1">{{ $t('dashboard.overview') }}</p>
        </div>
        <div class="text-sm text-gray-500 dark:text-gray-400">
          {{ new Date().toLocaleDateString() }}
        </div>
      </div>

      <!-- Stats Grid -->
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-4">
          <div class="p-3 bg-blue-100 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('dashboard.totalStudents') }}</p>
            <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ dashboardStats.total_students }}</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-4">
          <div class="p-3 bg-indigo-100 dark:bg-indigo-900/30 text-indigo-600 dark:text-indigo-400 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('dashboard.totalRooms') }}</p>
            <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ dashboardStats.total_rooms }}</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-4">
          <div class="p-3 bg-green-100 dark:bg-green-900/30 text-green-600 dark:text-green-400 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('dashboard.inspectionsToday') }}</p>
            <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ dashboardStats.inspections_today }}</p>
          </div>
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 flex items-center space-x-4">
          <div class="p-3 bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 rounded-xl">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-8 w-8" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
            </svg>
          </div>
          <div>
            <p class="text-sm text-gray-500 dark:text-gray-400">{{ $t('dashboard.issuesFound') }}</p>
            <p class="text-2xl font-bold text-gray-800 dark:text-white">{{ dashboardStats.issues_found }}</p>
          </div>
        </div>
      </div>

      <div class="grid grid-cols-1 lg:grid-cols-3 gap-8">
        <!-- Recent Inspections -->
        <div class="lg:col-span-2 bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center">
            <h3 class="text-lg font-bold text-gray-800 dark:text-white">{{ $t('dashboard.recentInspections') }}</h3>
            <NuxtLink :to="localePath('/admin/inspections')" class="text-sm text-primary-600 hover:text-primary-700 font-medium">
              {{ $t('dashboard.viewAll') }}
            </NuxtLink>
          </div>
          <div class="overflow-x-auto">
            <table class="w-full text-left">
              <thead>
                <tr class="bg-gray-50 dark:bg-gray-700/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                  <th class="px-6 py-4 font-medium">{{ $t('dashboard.room') }}</th>
                  <th class="px-6 py-4 font-medium">{{ $t('dashboard.inspector') }}</th>
                  <th class="px-6 py-4 font-medium">{{ $t('dashboard.date') }}</th>
                  <th class="px-6 py-4 font-medium">{{ $t('dashboard.status') }}</th>
                </tr>
              </thead>
              <tbody class="divide-y divide-gray-100 dark:divide-gray-700">
                <tr v-for="inspection in dashboardStats.recent_inspections" :key="inspection.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
                  <td class="px-6 py-4 text-sm text-gray-800 dark:text-gray-200 font-medium">{{ inspection.room.room_number }}</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ inspection.student.full_name }}</td>
                  <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ new Date(inspection.created_at).toLocaleDateString() }}</td>
                  <td class="px-6 py-4">
                    <span :class="`px-2 py-1 text-xs font-semibold rounded-full ${getStatusColor(inspection.status)}`">
                      {{ $t(`inspection.status.${inspection.status}`) }}
                    </span>
                  </td>
                </tr>
                <tr v-if="dashboardStats.recent_inspections.length === 0">
                  <td colspan="4" class="px-6 py-8 text-center text-gray-500">
                    {{ $t('index.latestInspection.noRecord') }}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        <!-- Quick Actions -->
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
          <div class="p-6 border-b border-gray-100 dark:border-gray-700">
            <h3 class="text-lg font-bold text-gray-800 dark:text-white">{{ $t('dashboard.quickActions') }}</h3>
          </div>
          <div class="p-6 grid grid-cols-1 gap-4">
            <NuxtLink :to="localePath('/admin/new-inspection')" class="flex items-center p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl hover:bg-primary-100 dark:hover:bg-primary-900/40 transition-colors group">
              <div class="p-2 bg-primary-100 dark:bg-primary-800 rounded-lg text-primary-600 dark:text-primary-200 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4" />
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-primary-700 dark:group-hover:text-primary-300">{{ $t('dashboard.newInspection') }}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">Start a new inspection</p>
              </div>
            </NuxtLink>
            
            <NuxtLink :to="localePath('/admin/students')" class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
              <div class="p-2 bg-gray-200 dark:bg-gray-600 rounded-lg text-gray-600 dark:text-gray-300 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z" />
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-gray-900 dark:group-hover:text-white">{{ $t('dashboard.manageStudents') }}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">View and edit students</p>
              </div>
            </NuxtLink>

            <NuxtLink :to="localePath('/admin/rooms')" class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
              <div class="p-2 bg-gray-200 dark:bg-gray-600 rounded-lg text-gray-600 dark:text-gray-300 mr-4">
                <svg xmlns="http://www.w3.org/2000/svg" class="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                </svg>
              </div>
              <div>
                <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-gray-900 dark:group-hover:text-white">{{ $t('dashboard.manageRooms') }}</h4>
                <p class="text-xs text-gray-500 dark:text-gray-400">View and edit rooms</p>
              </div>
            </NuxtLink>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, reactive } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useLocalePath } from '#imports';
import { useI18n } from 'vue-i18n';

const { isAuthenticated, hasPermission, user, apiFetch } = useAuth();
const localePath = useLocalePath();
const { t } = useI18n();

const latestInspection = ref(null);
const dashboardStats = reactive({
  total_students: 0,
  total_rooms: 0,
  inspections_today: 0,
  issues_found: 0,
  recent_inspections: []
});

const isStudent = computed(() => {
  return isAuthenticated.value && !hasPermission('admin:full_access');
});

const isAdmin = computed(() => {
  return isAuthenticated.value && hasPermission('admin:full_access');
});

const fetchLatestInspection = async () => {
  if (isStudent.value) {
    try {
      const response = await apiFetch('/api/v1/inspections?limit=1');
      if (response && response.records && response.records.length > 0) {
        latestInspection.value = response.records[0];
      }
    } catch (error) {
      console.error("Failed to fetch latest inspection:", error);
    }
  }
};

const fetchDashboardStats = async () => {
  if (isAdmin.value) {
    try {
      const response = await apiFetch('/api/v1/admin/dashboard-stats');
      if (response) {
        dashboardStats.total_students = response.total_students;
        dashboardStats.total_rooms = response.total_rooms;
        dashboardStats.inspections_today = response.inspections_today;
        dashboardStats.issues_found = response.issues_found;
        dashboardStats.recent_inspections = response.recent_inspections;
      }
    } catch (error) {
      console.error("Failed to fetch dashboard stats:", error);
    }
  }
};

const getStatusColor = (status: string) => {
  switch (status) {
    case 'approved':
      return 'bg-green-100 text-green-800 dark:bg-green-900/50 dark:text-green-300';
    case 'submitted':
      return 'bg-blue-100 text-blue-800 dark:bg-blue-900/50 dark:text-blue-300';
    case 'pending':
      return 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/50 dark:text-yellow-300';
    default:
      return 'bg-gray-100 text-gray-800 dark:bg-gray-700 dark:text-gray-300';
  }
};

onMounted(() => {
  if (isStudent.value) {
    fetchLatestInspection();
  } else if (isAdmin.value) {
    fetchDashboardStats();
  }
});
</script>
