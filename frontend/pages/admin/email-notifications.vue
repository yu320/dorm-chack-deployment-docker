<template>
  <div class="p-4 sm:p-6">
    <div class="max-w-7xl mx-auto">
      <div class="bg-white dark:bg-gray-800 shadow-md rounded-lg p-6">
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white mb-4">
          {{ $t('admin.emailNotifications.title') }}
        </h1>
        <p class="text-gray-600 dark:text-gray-400 mb-6">
          {{ $t('admin.emailNotifications.description') }}
        </p>

        <div class="space-y-6">
          <div>
            <label for="recipients" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.recipientsLabel') }}</label>
            <select id="recipients" v-model="recipientType" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option value="all_students">{{ $t('admin.emailNotifications.allStudents') }}</option>
              <option value="students_in_building">{{ $t('admin.emailNotifications.studentsInBuilding') }}</option>
              <option value="students_in_room">{{ $t('admin.emailNotifications.studentsInRoom') }}</option>
              <option value="students_in_household">{{ $t('admin.emailNotifications.studentsInHousehold') }}</option>
              <option value="custom">{{ $t('admin.emailNotifications.customRecipients') }}</option>
            </select>
          </div>

          <!-- Conditional selectors based on recipientType -->
          <div v-if="recipientType === 'students_in_building'">
            <label for="building-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.selectBuilding') }}</label>
            <select id="building-select" v-model="selectedBuildingId" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option :value="null">{{ $t('admin.selectBuildingPrompt') }}</option>
              <option v-for="building in buildings" :key="building.id" :value="building.id">{{ building.name }}</option>
            </select>
          </div>

          <div v-if="recipientType === 'students_in_room'">
            <label for="room-select" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.selectRoom') }}</label>
            <select id="room-select" v-model="selectedRoomId" class="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-primary-500 focus:border-primary-500 sm:text-sm rounded-md">
              <option :value="null">{{ $t('admin.selectRoomPrompt') }}</option>
              <option v-for="room in rooms" :key="room.id" :value="room.id">{{ room.room_number }} ({{ room.building.name }})</option>
            </select>
          </div>

          <div v-if="recipientType === 'students_in_household'">
            <label for="household-input" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.selectHousehold') }}</label>
            <input type="text" id="household-input" v-model="selectedHousehold" :placeholder="$t('admin.householdOptional')" class="mt-1 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300 rounded-md">
          </div>

          <div v-if="recipientType === 'custom'">
            <label for="custom-recipients" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.customRecipientsLabel') }}</label>
            <input type="text" id="custom-recipients" v-model="customRecipientsInput" :placeholder="$t('admin.emailNotifications.customRecipientsPlaceholder')" class="mt-1 block w-full shadow-sm focus:ring-primary-500 focus:border-primary-500 sm:text-sm border-gray-300 rounded-md">
          </div>

          <div>
            <label for="subject" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.subjectLabel') }}</label>
            <div class="mt-1">
              <input type="text" name="subject" id="subject" v-model="subject" class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md" :placeholder="$t('admin.emailNotifications.subjectPlaceholder')">
            </div>
          </div>

          <div>
            <label for="message" class="block text-sm font-medium text-gray-700 dark:text-gray-300">{{ $t('admin.emailNotifications.messageLabel') }}</label>
            <div class="mt-1">
              <textarea id="message" name="message" rows="10" v-model="body" class="shadow-sm focus:ring-primary-500 focus:border-primary-500 block w-full sm:text-sm border-gray-300 rounded-md" :placeholder="$t('admin.emailNotifications.messagePlaceholder')"></textarea>
            </div>
          </div>
        </div>

        <div class="mt-6">
          <button type="button" @click="sendEmail" :disabled="loading" class="w-full bg-primary-600 hover:bg-primary-700 text-white font-medium py-2 px-4 rounded-lg disabled:bg-gray-400 disabled:cursor-not-allowed">
            <span v-if="loading">{{ $t('loading') }}</span>
            <span v-else>{{ $t('admin.emailNotifications.sendEmailButton') }}</span>
          </button>
        </div>


      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue';
import { useI18n } from 'vue-i18n';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import type { Building, Room } from '~/types';

definePageMeta({
  permission: 'manage_users',
});

const { t } = useI18n();
const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();

const recipientType = ref<'all_students' | 'students_in_building' | 'students_in_room' | 'students_in_household' | 'custom'>('all_students');
const selectedBuildingId = ref<number | null>(null);
const selectedRoomId = ref<number | null>(null);
const selectedHousehold = ref<string>('');
const customRecipientsInput = ref<string>('');
const subject = ref<string>('');
const body = ref<string>('');
const buildings = ref<Building[]>([]);
const rooms = ref<Room[]>([]);
const loading = ref(false);

const fetchBuildings = async () => {
  try {
    const response = await apiFetch('/api/v1/buildings');
    buildings.value = response as Building[];
  } catch (error) {

    showSnackbar({ message: t('snackbar.failedToLoadBuildings'), type: 'error' });
  }
};

const fetchRooms = async () => {
  try {
    const response = await apiFetch('/api/v1/rooms');
    rooms.value = response as Room[];
  } catch (error) {

    showSnackbar({ message: t('snackbar.failedToLoadData'), type: 'error' });
  }
};

const sendEmail = async () => {
  loading.value = true;
  try {
    const payload: { [key: string]: any } = {
      recipient_type: recipientType.value,
      subject: subject.value,
      body: body.value,
    };

    if (recipientType.value === 'students_in_building') {
      payload.building_id = selectedBuildingId.value;
    } else if (recipientType.value === 'students_in_room') {
      payload.room_id = selectedRoomId.value;
    } else if (recipientType.value === 'students_in_household') {
      payload.household = selectedHousehold.value;
    } else if (recipientType.value === 'custom') {
      payload.custom_recipients = customRecipientsInput.value.split(',').map(email => email.trim()).filter(email => email);
    }

    await apiFetch('/api/v1/notifications/send-email', {
      method: 'POST',
      body: payload,
    });

    showSnackbar({ message: t('admin.emailNotifications.sendEmailSuccess'), type: 'success' });
    // Reset form
    recipientType.value = 'all_students';
    selectedBuildingId.value = null;
    selectedRoomId.value = null;
    selectedHousehold.value = '';
    customRecipientsInput.value = '';
    subject.value = '';
    body.value = '';

  } catch (error: any) {

    const errorMessage = error.response?._data?.detail || t('admin.emailNotifications.sendEmailFailed');
    showSnackbar({ message: errorMessage, type: 'error' });
  } finally {
    loading.value = false;
  }
};

onMounted(() => {
  fetchBuildings();
  fetchRooms();
});

// Reset selectors when recipient type changes
watch(recipientType, (newType) => {
  if (newType !== 'students_in_building') {
    selectedBuildingId.value = null;
  }
  if (newType !== 'students_in_room') {
    selectedRoomId.value = null;
  }
  if (newType !== 'students_in_household') {
    selectedHousehold.value = '';
  }
  if (newType !== 'custom') {
    customRecipientsInput.value = '';
  }
});
</script>
