<template>
  <div class="relative w-full max-w-md">
    <input
      type="text"
      v-model="searchQuery"
      :placeholder="$t('globalSearch.placeholder')"
      class="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md shadow-sm focus:ring-primary-500 focus:border-primary-500 bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
      @focus="showResults = true"
      @blur="hideResultsTemporarily"
      @keydown.esc="showResults = false"
    />
    <div class="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
      <svg class="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
      </svg>
    </div>

    <div v-if="isLoading" class="absolute z-10 w-full bg-white dark:bg-gray-800 shadow-lg rounded-md mt-1 p-2">
      <p class="text-gray-500 dark:text-gray-400">{{ $t('globalSearch.loading') }}</p>
    </div>

    <ul
      v-if="showResults && !isLoading && searchResults.length > 0"
      class="absolute z-10 w-full bg-white dark:bg-gray-800 shadow-lg rounded-md mt-1 max-h-60 overflow-auto ring-1 ring-black ring-opacity-5 focus:outline-none"
    >
      <li v-for="item in searchResults" :key="item.id" @mousedown.prevent="selectResult(item)" class="cursor-pointer select-none relative py-2 pl-3 pr-9 hover:bg-primary-50 dark:hover:bg-primary-900 text-gray-900 dark:text-white">
        <div class="flex items-center">
          <span class="font-medium truncate">{{ item.title }}</span>
          <span v-if="item.description" class="ml-2 text-gray-500 dark:text-gray-400 text-sm">{{ item.description }}</span>
        </div>
        <span class="absolute inset-y-0 right-0 flex items-center pr-4 text-gray-400 text-xs capitalize">{{ item.type }}</span>
      </li>
    </ul>
    <div v-else-if="showResults && !isLoading && searchQuery.length >= 2 && searchResults.length === 0" class="absolute z-10 w-full bg-white dark:bg-gray-800 shadow-lg rounded-md mt-1 p-2">
      <p class="text-gray-500 dark:text-gray-400">{{ $t('globalSearch.noResults') }}</p>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue';
import { useRouter } from 'vue-router';
import { useGlobalSearch } from '~/composables/useGlobalSearch';
import { useI18n } from 'vue-i18n';

interface SearchResultItem {
  type: string; // e.g., "student", "room"
  id: string; // UUID for student, int for room
  title: string; // Display name
  description?: string; // Additional info
}

const { searchQuery, searchResults, isLoading } = useGlobalSearch();
const router = useRouter();
const { t } = useI18n();

const showResults = ref(false);
let blurTimeout: ReturnType<typeof setTimeout> | null = null;

const selectResult = (item: SearchResultItem) => {
  if (item.type === 'student') {
    router.push(`/admin/students?id=${item.id}`); // Assuming a student detail page or filter
  } else if (item.type === 'room') {
    router.push(`/admin/rooms?id=${item.id}`); // Assuming a room detail page or filter
  }
  showResults.value = false;
  searchQuery.value = ''; // Clear search query after selection
};

const hideResultsTemporarily = () => {
  blurTimeout = setTimeout(() => {
    showResults.value = false;
  }, 150); // Delay hiding to allow click event on result item
};

// Clear timeout if component is unmounted
onUnmounted(() => {
  if (blurTimeout) {
    clearTimeout(blurTimeout);
  }
});
</script>