<template>
  <div v-if="inspection" class="max-w-4xl mx-auto space-y-8">
    <!-- Header Card -->
    <div class="bg-white p-8 rounded-lg shadow-lg border border-gray-200">
      <div class="flex justify-between items-center mb-4">
        <h1 class="text-3xl font-bold text-gray-800">{{ $t('inspection.detailsTitle') }} #{{ inspection.id }}</h1>
        <NuxtLink to="/admin/inspections" class="text-primary-600 hover:text-primary-800 flex items-center">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 19l-7-7m0 0l7-7m-7 7h18" /></svg>
          {{ $t('inspection.backToInspections') }}
        </NuxtLink>
      </div>
      <p class="text-gray-600 mt-2">{{ $t('inspection.detailedView') }}</p>
    </div>

    <!-- Inspection Summary -->
    <div class="bg-white p-8 rounded-lg shadow-lg border border-gray-200">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ $t('inspection.summary') }}</h2>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500">{{ $t('inspection.studentName') }}:</p>
          <p class="text-lg font-semibold text-gray-900">{{ inspection.student.full_name }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500">{{ $t('inspection.roomNumber') }}:</p>
          <p class="text-lg font-semibold text-gray-900">{{ inspection.room.room_number }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500">{{ $t('dashboard.status') }}:</p>
          <p class="text-lg font-semibold" :class="{ 'text-green-600': inspection.status === 'approved', 'text-yellow-600': inspection.status === 'submitted', 'text-red-600': inspection.status === 'pending' }">{{ $t('inspection.status.' + inspection.status) }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg">
          <p class="text-sm font-medium text-gray-500">{{ $t('inspection.submittedAt') }}:</p>
          <p v-if="inspection.submitted_at" class="text-lg font-semibold text-gray-900">{{ new Date(inspection.submitted_at).toLocaleString() }}</p>
          <p v-else class="text-lg font-semibold text-gray-500">{{ $t('inspection.status.notSubmitted') }}</p>
        </div>
        <div class="bg-gray-50 p-4 rounded-lg" v-if="inspection.inspector">
          <p class="text-sm font-medium text-gray-500">{{ $t('admin.inspector') }}:</p>
          <p class="text-lg font-semibold text-gray-900">{{ inspection.inspector.username }}</p>
        </div>
      </div>
    </div>

    <!-- Inspected Items -->
    <div class="bg-white p-8 rounded-lg shadow-lg border border-gray-200">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ $t('inspection.inspectionItems') }}</h2>
      <div class="space-y-6">
        <div v-for="item in inspection.details" :key="item.id" class="p-6 border border-gray-200 rounded-lg shadow-sm">
          <h3 class="text-xl font-semibold text-gray-800 mb-2">{{ $t('items.' + item.item.name.toLowerCase()) }}</h3>
          <p class="text-gray-600">{{ $t('dashboard.status') }}: <span :class="item.status === 'ok' ? 'text-green-600' : 'text-red-600'">{{ $t('inspection.status.' + item.status) }}</span></p>
          <p v-if="item.comment" class="text-gray-600 mt-1">{{ $t('inspection.comment') }}: {{ item.comment }}</p>
          <div v-if="item.photos && item.photos.length > 0" class="mt-4 grid grid-cols-3 gap-4">
            <div v-for="photo in item.photos" :key="photo.id">
              <img :src="photo.file_path" :alt="item.item.name" class="max-w-xs h-auto rounded-lg shadow-md border border-gray-200">
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Signature -->
    <div class="bg-white p-8 rounded-lg shadow-lg border border-gray-200">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ $t('inspection.studentSignature') }}</h2>
      <div class="border rounded-lg p-4 bg-gray-50 flex justify-center items-center">
        <img :src="inspection.signature" alt="Student Signature" class="max-w-full h-auto rounded-md shadow-sm">
      </div>
    </div>

    <!-- Admin Actions -->
    <div class="bg-white p-8 rounded-lg shadow-lg border border-gray-200">
      <h2 class="text-2xl font-bold text-gray-800 mb-4">{{ $t('admin.adminActions') }}</h2>
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-8">
        <!-- Update Status -->
        <div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ $t('admin.updateStatus') }}</h3>
          <div class="flex space-x-4">
            <select v-model="newStatus" class="block w-full border border-gray-300 bg-white text-gray-900 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500">
              <option value="approved">{{ $t('inspection.status.approved') }}</option>
              <option value="rejected">{{ $t('inspection.status.rejected') }}</option>
              <option value="pending">{{ $t('inspection.status.pending') }}</option>
            </select>
            <button @click="updateStatus" class="bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200">
              {{ $t('admin.update') }}
            </button>
          </div>
        </div>

        <!-- Email Report -->
        <div>
          <h3 class="text-lg font-semibold text-gray-700 mb-2">{{ $t('admin.emailReport') }}</h3>
          <div class="flex space-x-4">
            <input type="email" v-model="recipientEmail" :placeholder="$t('admin.recipientEmailPlaceholder')" class="block w-full border border-gray-300 bg-white text-gray-900 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-primary-500 focus:border-primary-500">
            <button @click="emailReport" class="bg-green-600 hover:bg-green-700 text-white font-medium py-2 px-4 rounded-lg transition duration-200 whitespace-nowrap">
              {{ $t('admin.sendEmail') }}
            </button>
          </div>
        </div>
      </div>

      <!-- Export PDF -->
      <div class="mt-8 pt-6 border-t border-gray-200">
        <a :href="`/api/v1/inspections/${inspection.id}/pdf`" target="_blank" class="inline-flex items-center text-primary-600 hover:text-primary-800 font-medium">
          <svg xmlns="http://www.w3.org/2000/svg" class="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          {{ $t('records.downloadPdf') }}
        </a>
      </div>
    </div>
  </div>
  <div v-else class="text-center">
    <p>Loading inspection details...</p>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useAuth } from '~/composables/useAuth'
import { useSnackbar } from '~/composables/useSnackbar'
import { useI18n } from 'vue-i18n';

definePageMeta({
  permission: 'inspections:view',
});

const { t } = useI18n();
const route = useRoute()
const { apiFetch } = useAuth()
const { showSnackbar } = useSnackbar()

const inspection = ref<any>(null)
const newStatus = ref('pending')
const recipientEmail = ref('')

const fetchInspection = async () => {
  const id = route.params.id
  try {
    const response = await apiFetch(`/api/v1/inspections/${id}`)
    inspection.value = response
    newStatus.value = response.status
  } catch (error) {
    showSnackbar({ message: 'Failed to load inspection details.', type: 'error' })
  }
}

const updateStatus = async () => {
  try {
    await apiFetch(`/api/v1/inspections/${inspection.value.id}`, {
      method: 'PUT',
      body: { status: newStatus.value }
    })
    inspection.value.status = newStatus.value
    showSnackbar({ message: t('snackbar.statusUpdated'), type: 'success' })
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToUpdateStatus'), type: 'error' })
  }
}

const emailReport = async () => {
  if (!recipientEmail.value) {
    showSnackbar({ message: t('snackbar.enterRecipientEmail'), type: 'error' })
    return
  }
  try {
    await apiFetch(`/api/v1/inspections/${inspection.value.id}/email`, {
      method: 'POST',
      body: { recipient_email: recipientEmail.value }
    })
    showSnackbar({ message: t('snackbar.reportEmailed'), type: 'success' })
    recipientEmail.value = ''
  } catch (error) {
    showSnackbar({ message: t('snackbar.failedToEmailReport'), type: 'error' })
  }
}

onMounted(fetchInspection)
</script>
