<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 transition-colors duration-300">
    <!-- 1. Guest View (Public) -->
    <GuestHome v-if="!isAuthenticated" />

    <!-- 2. Authenticated View -->
    <div v-else class="container mx-auto px-4 py-8">
      
      <!-- Loading Skeleton -->
      <CommonDashboardSkeleton v-if="pending" />

      <!-- Role-Based Content -->
      <template v-else>
        <!-- Admin Dashboard -->
        <AdminDashboard 
          v-if="isAdmin" 
          :stats="dashboardData"
        />

        <!-- Student Dashboard -->
        <StudentDashboard 
          v-else 
          :user="user" 
          :latest-inspection="dashboardData?.latestInspection"
        />
      </template>

    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useDashboardData } from '~/composables/useDashboardData';

// Composables
const { isAuthenticated, hasPermission, user } = useAuth();
const { data: dashboardData, pending } = useDashboardData();

// Computed Roles
const isAdmin = computed(() => hasPermission('admin:full_access'));

// Head Management (SEO)
useHead({
  title: computed(() => isAuthenticated.value ? 'Dashboard - DormManager' : 'Welcome - DormManager')
});
</script>