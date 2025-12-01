<template>
  <div class="min-h-screen bg-slate-50 dark:bg-gray-900 flex flex-col">
    <TheHeader />
    <main class="container mx-auto p-4 flex-grow">
      <slot />
    </main>
    <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4 mt-8">
      <div class="container mx-auto text-center text-sm text-gray-500 dark:text-gray-400">
        <p class="mb-2">{{ $t('footer.copyright', { year: new Date().getFullYear() }) }}</p>
        <p class="flex justify-center items-center gap-2">
          <Icon name="heroicons:phone" class="w-4 h-4" />
          <span> 05-534-2601 #2097</span>
        </p>
      </div>
    </footer>
    <Snackbar />
  </div>
</template>

<script setup lang="ts">
import TheHeader from '~/components/layout/TheHeader.vue'
import Snackbar from '~/components/common/Snackbar.vue'
</script>
