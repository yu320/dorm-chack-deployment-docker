<template>
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
        <tr v-for="inspection in data" :key="inspection.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/50 transition-colors">
          <td class="px-6 py-4 text-sm text-gray-800 dark:text-gray-200 font-medium">{{ inspection.room.room_number }}</td>
          <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ inspection.student.full_name }}</td>
          <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400">{{ new Date(inspection.created_at).toLocaleDateString() }}</td>
          <td class="px-6 py-4">
            <CommonStatusBadge :status="inspection.status" />
          </td>
        </tr>
        <tr v-if="data.length === 0">
          <td colspan="4" class="px-6 py-8 text-center text-gray-500">
            {{ $t('index.latestInspection.noRecord') }}
          </td>
        </tr>
      </tbody>
    </table>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  data: any[];
}>();
</script>