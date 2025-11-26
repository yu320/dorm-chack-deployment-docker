import { ref, watch } from 'vue';
import { useDebounceFn } from '@vueuse/core';
import { useAuth } from '~/composables/useAuth'; // Import useAuth

interface SearchResultItem {
  type: string;
  id: string;
  title: string;
  description?: string;
}

export function useGlobalSearch() {
  const searchQuery = ref('');
  const searchResults = ref<SearchResultItem[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  const { apiFetch } = useAuth(); // Get apiFetch from useAuth

  const performSearch = useDebounceFn(async () => {
    const query = searchQuery.value.trim();
    if (query.length < 2) {
      searchResults.value = [];
      error.value = null;
      return;
    }

    isLoading.value = true;
    error.value = null;

    try {
      const response = await apiFetch('/api/v1/search', { // Use apiFetch
        method: 'POST',
        body: { query },
      });
      searchResults.value = response.results || [];
    } catch (e: any) {
      error.value = e.data?.detail || 'Failed to perform search.';
      searchResults.value = [];
    } finally {
      isLoading.value = false;
    }
  }, 300);

  watch(searchQuery, () => {
    performSearch();
  });

  return {
    searchQuery,
    searchResults,
    isLoading,
    error,
  };
}
