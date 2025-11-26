<script setup lang="ts">
import { ref, watch, computed, onMounted, onUnmounted } from 'vue';
import { useI18n } from '#imports';

const { t } = useI18n();

interface Bed {
  id: number;
  bed_number: string;
  status: string;
}
interface Room {
  id: number;
  room_number: string;
  beds: Bed[];
}
interface Building {
  id: number;
  name: string;
  rooms: Room[];
}

const props = defineProps<{
  options: Building[];
  modelValue: number | null;
  originalBedId?: number | null;
  placeholder?: string;
  loading?: boolean;
}>();

const emit = defineEmits(['update:modelValue']);

const isOpen = ref(false);
const dropdownRef = ref<HTMLElement | null>(null);

const findBedInfo = (bedId: number | null) => {
  if (!bedId) return null;
  for (const building of props.options) {
    for (const room of building.rooms) {
      const bed = room.beds.find(b => b.id === bedId);
      if (bed) {
        return { building, room, bed };
      }
    }
  }
  return null;
};

const selectedLabel = computed(() => {
  const info = findBedInfo(props.modelValue);
  if (!info) return props.placeholder || t('admin.selectBed');
  return `${info.building.name} - ${info.room.room_number} - ${info.bed.bed_number}`;
});

const selectBed = (bed: Bed, building: Building, room: Room) => {
  if (bed.status !== 'available' && bed.id !== props.originalBedId) {
    return;
  }
  emit('update:modelValue', bed.id);
  isOpen.value = false;
};

const handleClickOutside = (event: MouseEvent) => {
  if (dropdownRef.value && !dropdownRef.value.contains(event.target as Node)) {
    isOpen.value = false;
  }
};

onMounted(() => {
  document.addEventListener('click', handleClickOutside);
});

onUnmounted(() => {
  document.removeEventListener('click', handleClickOutside);
});
</script>
<template>
  <div class="relative" ref="dropdownRef">
    <button
      type="button"
      @click="isOpen = !isOpen"
      class="relative w-full cursor-default rounded-md bg-white dark:bg-gray-700 py-2 pl-3 pr-10 text-left text-gray-900 dark:text-gray-200 shadow-sm ring-1 ring-inset ring-gray-300 dark:ring-gray-600 focus:outline-none focus:ring-2 focus:ring-primary-600 sm:text-sm sm:leading-6"
    >
      <span class="block truncate">{{ selectedLabel || placeholder }}</span>
      <span class="pointer-events-none absolute inset-y-0 right-0 flex items-center pr-2">
        <svg class="h-5 w-5 text-gray-400" viewBox="0 0 20 20" fill="currentColor" aria-hidden="true">
          <path fill-rule="evenodd" d="M10 3a.75.75 0 01.75.75v10.5a.75.75 0 01-1.5 0V3.75A.75.75 0 0110 3z" clip-rule="evenodd" />
        </svg>
      </span>
    </button>

    <transition
      leave-active-class="transition ease-in duration-100"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div v-if="isOpen" class="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white dark:bg-gray-800 py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
        <ul>
          <li v-if="options.length === 0" class="relative cursor-default select-none py-2 px-4 text-gray-700 dark:text-gray-400">
            {{ loading ? $t('loading') : $t('noOptions') }}
          </li>
          <template v-for="building in options" :key="building.id">
            <li class="px-3 py-2 text-xs font-semibold text-gray-500 dark:text-gray-400 bg-gray-50 dark:bg-gray-700/50 sticky top-0">
              {{ building.name }}
            </li>
            <template v-for="room in building.rooms" :key="room.id">
               <li class="pl-6 pr-3 py-2 text-xs font-medium text-gray-600 dark:text-gray-300">
                {{ room.room_number }}
              </li>
              <li
                v-for="bed in room.beds"
                :key="bed.id"
                @click="selectBed(bed, building, room)"
                :class="[
                  'relative cursor-pointer select-none py-2 pl-10 pr-4',
                  modelValue === bed.id ? 'bg-primary-600 text-white' : 'text-gray-900 dark:text-gray-200 hover:bg-primary-50 dark:hover:bg-gray-700',
                  (bed.status !== 'available' && bed.id !== originalBedId) ? 'opacity-50 cursor-not-allowed' : ''
                ]"
              >
                <span :class="['block truncate', modelValue === bed.id ? 'font-semibold' : 'font-normal']">
                  {{ bed.bed_number }} ({{ $t(`admin.${bed.status.toLowerCase()}`) }})
                </span>
              </li>
            </template>
          </template>
        </ul>
      </div>
    </transition>
  </div>
</template>
