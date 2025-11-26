<template>
  <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
    <div class="p-6 border-b border-gray-100 dark:border-gray-700">
      <h3 class="text-lg font-bold text-gray-800 dark:text-white">{{ $t('dashboard.quickActions') }}</h3>
    </div>
    <div class="p-6 grid grid-cols-1 gap-4">
      <NuxtLink :to="localePath('/admin/new-inspection')" class="flex items-center p-4 bg-primary-50 dark:bg-primary-900/20 rounded-xl hover:bg-primary-100 dark:hover:bg-primary-900/40 transition-colors group">
        <div class="p-2 bg-primary-100 dark:bg-primary-800 rounded-lg text-primary-600 dark:text-primary-200 mr-4">
          <Icon name="heroicons:clipboard-document-check" class="h-6 w-6" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-primary-700 dark:group-hover:text-primary-300">{{ $t('dashboard.newInspection') }}</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">Start a new inspection</p>
        </div>
      </NuxtLink>
      
      <NuxtLink :to="localePath('/admin/students')" class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
        <div class="p-2 bg-gray-200 dark:bg-gray-600 rounded-lg text-gray-600 dark:text-gray-300 mr-4">
          <Icon name="heroicons:users" class="h-6 w-6" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-gray-900 dark:group-hover:text-white">{{ $t('dashboard.manageStudents') }}</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">View and edit students</p>
        </div>
      </NuxtLink>

      <NuxtLink :to="localePath('/admin/rooms')" class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
        <div class="p-2 bg-gray-200 dark:bg-gray-600 rounded-lg text-gray-600 dark:text-gray-300 mr-4">
          <Icon name="heroicons:key" class="h-6 w-6" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-gray-900 dark:group-hover:text-white">{{ $t('dashboard.manageRooms') }}</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">View and edit rooms</p>
        </div>
      </NuxtLink>

      <NuxtLink :to="localePath('/admin/announcements')" class="flex items-center p-4 bg-gray-50 dark:bg-gray-700/30 rounded-xl hover:bg-gray-100 dark:hover:bg-gray-700/50 transition-colors group">
        <div class="p-2 bg-gray-200 dark:bg-gray-600 rounded-lg text-gray-600 dark:text-gray-300 mr-4">
          <Icon name="heroicons:megaphone" class="h-6 w-6" />
        </div>
        <div>
          <h4 class="font-semibold text-gray-800 dark:text-white group-hover:text-gray-900 dark:group-hover:text-white">公告管理</h4>
          <p class="text-xs text-gray-500 dark:text-gray-400">發布與管理公告</p>
        </div>
      </NuxtLink>
    </div>
  </div>
</template>

<script setup lang="ts">
const localePath = useLocalePath();
</script>