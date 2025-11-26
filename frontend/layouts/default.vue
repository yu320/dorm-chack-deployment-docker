<template>
  <div class="min-h-screen bg-slate-50 dark:bg-gray-900 flex flex-col">
    <TheHeader />
    <main class="container mx-auto p-4 flex-grow">
      <Transition name="page" mode="out-in">
        <slot />
      </Transition>
    </main>
    <footer class="bg-white dark:bg-gray-800 border-t border-gray-200 dark:border-gray-700 py-4 mt-8">
      <div class="container mx-auto text-center text-sm text-gray-500 dark:text-gray-400">
        <p>{{ $t('footer.copyright', { year: new Date().getFullYear() }) }}</p>
      </div>
    </footer>
    <Snackbar />
  </div>
</template>

<script setup lang="ts">
import TheHeader from '~/components/layout/TheHeader.vue'
import Snackbar from '~/components/common/Snackbar.vue'
</script>
