<template>
  <div class="min-h-[80vh] relative">
    <!-- Loading State -->
    <div v-if="isLoading" class="flex justify-center items-center h-64">
      <Icon name="lucide:loader-2" class="w-8 h-8 animate-spin text-primary-500" />
    </div>

    <!-- Step 1: Building Selection -->
    <div v-else-if="!selectedBuildingId" class="animate-in fade-in duration-500">
      <div class="mb-6 flex justify-between items-center">
        <h2 class="text-xl font-bold text-gray-800 dark:text-white">{{ $t('patrol.selectBuilding') }}</h2>
        <div class="flex items-center gap-2 bg-white dark:bg-gray-800 px-3 py-1 rounded-full shadow-sm border border-gray-100 dark:border-gray-700">
          <Icon name="lucide:user" class="w-4 h-4 text-primary-500" />
          <span class="text-sm font-medium text-gray-600 dark:text-gray-300">
            {{ user?.username }}
          </span>
        </div>
      </div>

      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <button
          v-for="building in buildings"
          :key="building.id"
          @click="selectBuilding(building)"
          class="group relative overflow-hidden bg-white dark:bg-gray-800 p-6 rounded-2xl shadow-sm border-2 border-transparent hover:border-primary-100 hover:shadow-xl transition-all duration-300 text-left"
        >
          <div class="absolute top-0 right-0 p-4 opacity-10 group-hover:opacity-20 transition-opacity transform group-hover:scale-110 duration-500">
            <Icon name="lucide:building" class="w-24 h-24 text-primary-600" />
          </div>
          <div class="relative z-10">
            <span class="inline-block p-3 rounded-xl bg-primary-50 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 mb-4 group-hover:bg-primary-600 group-hover:text-white transition-colors">
              <Icon name="lucide:building" class="w-6 h-6" />
            </span>
            <h3 class="text-2xl font-bold text-gray-800 dark:text-white mb-1">{{ building.name }}</h3>
            <p class="text-gray-500 dark:text-gray-400 text-sm font-medium">{{ $t('patrol.clickToStart') }}</p>
          </div>
        </button>
      </div>
    </div>

    <!-- Step 2: Location Inspection -->
    <div v-else class="relative pb-32">
      
      <!-- Sticky Header -->
      <div class="sticky top-16 z-30 bg-white/95 dark:bg-gray-900/95 backdrop-blur-md shadow-sm border-b border-gray-100 dark:border-gray-800 -mx-4 px-4 py-3 mb-4 transition-all">
        <div class="max-w-6xl mx-auto flex flex-col gap-3">
            <div class="flex items-center justify-between">
                <button 
                    @click="clearSelection"
                    class="flex items-center gap-1 text-gray-500 hover:text-gray-900 dark:text-gray-400 dark:hover:text-white transition-colors text-sm font-medium"
                >
                    <Icon name="lucide:arrow-left" class="w-4 h-4" />
                    {{ $t('common.back') }}
                </button>
                
                <div class="flex items-center gap-2">
                    <span class="text-lg font-bold text-primary-600 dark:text-primary-400 bg-primary-50 dark:bg-primary-900/30 px-3 py-1 rounded-full">
                    {{ selectedBuilding?.name }}
                    </span>
                </div>
            </div>

            <!-- Floor Quick Jump -->
            <div v-if="floors.length > 0" class="flex gap-2 overflow-x-auto pb-1 no-scrollbar">
                <button
                    v-for="floor in floors"
                    :key="floor"
                    @click="scrollToFloor(floor)"
                    :class="[
                        'px-4 py-2 rounded-lg text-sm font-bold transition-all whitespace-nowrap active:scale-95',
                        activeFloor === floor
                            ? 'bg-gray-900 text-white dark:bg-white dark:text-gray-900 shadow-md ring-2 ring-offset-1 ring-gray-900 dark:ring-white'
                            : 'bg-gray-100 text-gray-500 hover:bg-gray-200 dark:bg-gray-800 dark:text-gray-400 dark:hover:bg-gray-700'
                    ]"
                >
                    {{ floor }}
                </button>
            </div>
        </div>
      </div>

      <!-- Loading Locations -->
      <div v-if="loadingData" class="flex flex-col items-center justify-center py-20 text-gray-400">
        <Icon name="lucide:loader-2" class="w-10 h-10 animate-spin text-primary-500 mb-3" />
        <p>{{ $t('common.loading') }}</p>
      </div>

      <!-- Inspection Grid (All Floors) -->
      <div v-else class="space-y-12 max-w-6xl mx-auto pt-4">
        <div v-if="Object.keys(householdsByFloor).length === 0" class="text-center py-10 text-gray-500">
            此建築物無資料。
        </div>

        <!-- Render by Floor -->
        <div 
            v-for="(floorHouseholds, floor) in householdsByFloor" 
            :key="floor"
            :id="`floor-${floor}`"
            class="scroll-mt-48" 
        >
            <!-- Floor Title -->
            <div class="flex items-center gap-4 mb-6 px-2">
                <h3 class="text-3xl font-black text-gray-200 dark:text-gray-700 select-none">{{ floor }}</h3>
                <div class="h-px bg-gray-100 dark:bg-gray-800 flex-1"></div>
            </div>

            <!-- Floor Cards Grid -->
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-2 xl:grid-cols-3 gap-6 px-2">
                <div 
                v-for="household in floorHouseholds"
                :key="household.name"
                class="bg-white dark:bg-gray-800 rounded-2xl p-5 shadow-sm border border-gray-100 dark:border-gray-700 hover:shadow-md transition-all duration-300"
                >
                <!-- Card Header -->
                <div class="flex justify-between items-start mb-5">
                    <h3 class="text-2xl font-bold text-gray-800 dark:text-white">
                    {{ household.name }}
                    </h3>
                    
                    <div 
                    :class="[
                        'px-3 py-1.5 rounded-lg text-xs font-bold flex items-center gap-1.5',
                        hasHouseholdViolation(household)
                        ? 'bg-red-100 text-red-600 dark:bg-red-900/40 dark:text-red-300'
                        : 'bg-green-100 text-green-600 dark:bg-green-900/40 dark:text-green-300'
                    ]"
                    >
                    <Icon :name="hasHouseholdViolation(household) ? 'lucide:alert-circle' : 'lucide:check-circle'" class="w-4 h-4" />
                    {{ hasHouseholdViolation(household) ? '異常' : '已關燈' }}
                    </div>
                </div>

                <!-- Action Buttons Grid -->
                <!-- Mobile optimized grid: 3 cols on mobile, 4 on desktop -->
                <div class="grid grid-cols-3 sm:grid-cols-4 gap-3">
                    <template v-for="space in household.spaces" :key="space.id">
                        <!-- Render buttons for each item in each space -->
                        <button
                            v-for="item in space.check_items"
                            :key="getItemKey(item)"
                            @click="toggleViolation(household.name, space.id, getItemKey(item))"
                            :class="[
                                'aspect-square flex flex-col items-center justify-center gap-1.5 rounded-xl transition-all duration-200 border relative overflow-hidden',
                                isViolationActive(household.name, space.id, getItemKey(item))
                                    ? 'bg-red-500 border-red-600 text-white shadow-lg scale-105 z-10' 
                                    : 'bg-gray-50 border-gray-100 text-gray-500 hover:bg-gray-100 hover:text-gray-700 dark:bg-gray-700/50 dark:border-gray-700 dark:text-gray-400'
                            ]"
                        >
                            <!-- Icon -->
                            <Icon :name="getItemIcon(getItemLabel(item))" class="w-7 h-7 sm:w-6 sm:h-6" />
                            
                            <!-- Text: Display Space Name primarily -->
                            <span class="text-xs sm:text-[10px] font-bold truncate w-full text-center px-1 leading-tight">
                                {{ space.name }}
                            </span>
                            
                            <!-- Optional: Show item name if it's not generic 'light' -->
                            <!-- But user wants to know "Where", so space.name is key -->
                        </button>
                    </template>
                    
                    <div v-if="household.spaces.every(s => !s.check_items || s.check_items.length === 0)" class="col-span-3 sm:col-span-4 text-center py-6 text-gray-400 text-sm italic bg-gray-50 rounded-xl">
                        無檢查項目
                    </div>
                </div>

                </div>
            </div>
        </div>
      </div>

      <!-- Floating Action Bar -->
      <div class="fixed bottom-0 left-0 right-0 p-4 z-40 transition-transform duration-300 translate-y-0">
        <div class="max-w-2xl mx-auto bg-gray-900 dark:bg-black text-white rounded-2xl shadow-2xl p-4 flex items-center justify-between gap-4 border border-gray-800 dark:border-gray-700">
          <div class="flex items-center gap-3 pl-2">
            <div class="bg-primary-600 text-white font-bold h-12 w-12 rounded-full flex items-center justify-center text-lg shadow-lg ring-2 ring-primary-400 ring-offset-2 ring-offset-gray-900">
              {{ groupedHouseholds.length }}
            </div>
            <div class="flex flex-col">
              <span class="text-sm font-bold text-white">{{ $t('patrol.confirmInspection') }}</span>
              <span class="text-xs text-gray-400">
                {{ abnormalHouseholdCount > 0 
                  ? $t('patrol.violationSummary', { count: abnormalHouseholdCount, normal: groupedHouseholds.length - abnormalHouseholdCount }) 
                  : $t('patrol.allClear')
                }}
              </span>
            </div>
          </div>

          <div class="flex items-center gap-2">
            <button 
              v-if="abnormalHouseholdCount > 0"
              @click="clearViolations"
              class="p-3 text-gray-400 hover:text-white hover:bg-gray-800 rounded-xl transition-colors"
              :title="$t('common.clear')"
            >
              <Icon name="lucide:rotate-ccw" class="w-5 h-5" />
            </button>
            <div class="h-8 w-px bg-gray-700 mx-2"></div>
            <button
              @click="submitPatrol"
              :disabled="submitting"
              class="bg-white text-gray-900 hover:bg-gray-100 px-6 py-3 rounded-xl font-bold text-base flex items-center gap-2 shadow-lg active:scale-95 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              <Icon v-if="submitting" name="lucide:loader-2" class="w-5 h-5 animate-spin" />
              <Icon v-else name="lucide:clipboard-check" class="w-5 h-5" />
              {{ $t('common.submit') }}
            </button>
          </div>
        </div>
      </div>

    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, watch } from 'vue';
import { useBuildings } from '~/composables/useBuildings';
import { useRooms } from '~/composables/useRooms';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import type { Building } from '~/types';

const { t, locale } = useI18n();
const { user, apiFetch } = useAuth();
const { getBuildings, isLoading: loadingBuildings } = useBuildings();
const { getRooms } = useRooms();
const { showSnackbar } = useSnackbar();

type CheckItem = string | { name_zh: string; name_en: string };

interface PatrolLocation {
    id: string;
    name: string;
    household?: string; 
    building_id: number;
    check_items?: CheckItem[];
}

interface HouseholdRoomRef {
    name: string; 
    roomId: number; 
}

interface GroupedHousehold {
    name: string;
    roomId: number;
    spaces: PatrolLocation[];
}

// State
const buildings = ref<Building[]>([]);
const selectedBuildingId = ref<number | null>(null);
const selectedBuilding = computed(() => buildings.value.find(b => b.id === selectedBuildingId.value));

const patrolLocationConfigs = ref<PatrolLocation[]>([]); 
const householdRoomRefs = ref<HouseholdRoomRef[]>([]); 

const loadingData = ref(false);
const submitting = ref(false);
const activeFloor = ref<string>('');

const isLoading = computed(() => loadingBuildings.value);

// Computed: Group by Household
const groupedHouseholds = computed<GroupedHousehold[]>(() => {
    const groups: GroupedHousehold[] = [];

    householdRoomRefs.value.forEach(hhRef => {
        const applicableSpaces = patrolLocationConfigs.value.filter(config => {
            if (!config.household) return true; // Global
            const targets = config.household.split(',').map(s => s.trim());
            return targets.includes(hhRef.name);
        });

        if (applicableSpaces.length > 0) {
            groups.push({
                name: hhRef.name,
                roomId: hhRef.roomId,
                spaces: applicableSpaces
            });
        }
    });

    return groups;
});

// Floor Logic
const extractFloor = (name: string): string => {
    const match = name.match(/(\d+)/);
    if (!match) return '其他';
    
    const num = match[0];
    if (num.length >= 3) {
        return num.substring(0, num.length - 2) + 'F';
    } else if (num.length > 0) {
        return num.charAt(0) + 'F';
    }
    return '其他';
};

// Computed: Organize households by floor
const householdsByFloor = computed(() => {
    const groups: Record<string, GroupedHousehold[]> = {};
    
    groupedHouseholds.value.forEach(hh => {
        const floor = extractFloor(hh.name);
        if (!groups[floor]) groups[floor] = [];
        groups[floor].push(hh);
    });

    // Sort floors keys numerically
    const sortedKeys = Object.keys(groups).sort((a, b) => {
        const nA = parseInt(a);
        const nB = parseInt(b);
        if (isNaN(nA)) return 1;
        if (isNaN(nB)) return -1;
        return nA - nB;
    });

    const sortedGroups: Record<string, GroupedHousehold[]> = {};
    sortedKeys.forEach(key => {
        sortedGroups[key] = groups[key];
    });
    
    return sortedGroups;
});

const floors = computed(() => Object.keys(householdsByFloor.value));

// Scroll To Floor
const scrollToFloor = (floor: string) => {
    activeFloor.value = floor;
    const el = document.getElementById(`floor-${floor}`);
    if (el) {
        const headerOffset = 180; // Adjust for sticky header height
        const elementPosition = el.getBoundingClientRect().top;
        const offsetPosition = elementPosition + window.pageYOffset - headerOffset;
        
        window.scrollTo({
            top: offsetPosition,
            behavior: 'smooth'
        });
    }
};

// Violations: Key = "HouseholdName_LocationID", Value = Array<ItemKey>
const violations = ref<Record<string, string[]>>({});

// Fetch Buildings
onMounted(async () => {
  try {
    const buildingsData = await getBuildings({ limit: 100 });
    if (Array.isArray(buildingsData)) {
      buildings.value = buildingsData;
    } else if (buildingsData && buildingsData.records) {
      buildings.value = buildingsData.records;
    }
  } catch (e) {
    console.error('Error fetching buildings:', e);
  }
});

// Watch Selection
watch(selectedBuildingId, async (newId) => {
  if (!newId) {
    patrolLocationConfigs.value = [];
    householdRoomRefs.value = [];
    violations.value = {};
    activeFloor.value = '';
    return;
  }
  
  loadingData.value = true;
  try {
    const locResponse = await apiFetch(`/api/v1/patrol-locations/?building_id=${newId}`);
    patrolLocationConfigs.value = locResponse.records || [];

    const roomsResponse = await getRooms({ building_id: newId, limit: 2000 });
    const rooms = roomsResponse.records || [];
    
    const hhMap = new Map<string, number>();
    rooms.forEach((r: any) => {
        const hhName = r.household || r.room_number; 
        if (!hhMap.has(hhName)) {
            hhMap.set(hhName, r.id); 
        }
    });

    householdRoomRefs.value = Array.from(hhMap.entries())
        .map(([name, roomId]) => ({ name, roomId }))
        .sort((a, b) => a.name.localeCompare(b.name, undefined, { numeric: true }));

  } catch (e) {
    console.error(e);
    showSnackbar({ message: t('snackbar.failedToLoadData'), type: 'error' });
  } finally {
    loadingData.value = false;
  }
});

// Helper Functions
const selectBuilding = (building: Building) => {
  selectedBuildingId.value = building.id;
};

const clearSelection = () => {
  selectedBuildingId.value = null;
};

const getItemKey = (item: CheckItem): string => {
    if (typeof item === 'string') return item;
    return item.name_en; 
};

const getItemLabel = (item: CheckItem): string => {
    if (typeof item === 'string') return item;
    return locale.value === 'en' ? item.name_en : item.name_zh;
};

// Icon Mapping
const getItemIcon = (itemName: string) => {
  const lower = itemName.toLowerCase();
  // We are now using Space Name on button, so we might want icon based on space?
  // Actually, item name is still passed here.
  // But wait, user wants space name on button.
  // The button text uses `space.name`.
  // The icon should probably also reflect `space.name` if item is just "light".
  // But let's stick to item name for icon for now, or mix logic.
  // Since user said "inspecting lights", maybe icon is always bulb?
  if (lower.includes('light') || lower.includes('燈')) return 'lucide:lightbulb';
  // ... (other icons)
  return 'lucide:lightbulb'; // Default to lightbulb as requested
};

// Violation Logic
const toggleViolation = (householdName: string, patrolLocationId: string, itemKey: string) => {
  const unitKey = `${householdName}_${patrolLocationId}`;
  const current = violations.value[unitKey] || [];
  const exists = current.includes(itemKey);
  
  let updated;
  if (exists) {
    updated = current.filter(key => key !== itemKey);
  } else {
    updated = [...current, itemKey];
  }

  if (updated.length > 0) {
    violations.value = { ...violations.value, [unitKey]: updated };
  } else {
    const { [unitKey]: _, ...rest } = violations.value;
    violations.value = rest;
  }
};

const isViolationActive = (householdName: string, patrolLocationId: string, itemKey: string) => {
  const unitKey = `${householdName}_${patrolLocationId}`;
  return violations.value[unitKey]?.includes(itemKey);
};

const hasHouseholdViolation = (household: GroupedHousehold) => {
    const prefix = `${household.name}_`;
    return Object.keys(violations.value).some(k => k.startsWith(prefix));
};

const clearViolations = () => {
  violations.value = {};
};

const abnormalHouseholdCount = computed(() => {
    // Count households that have at least one violation
    let count = 0;
    groupedHouseholds.value.forEach(hh => {
        if (hasHouseholdViolation(hh)) {
            count++;
        }
    });
    return count;
});

// Submit
const submitPatrol = async () => {
  if (!selectedBuildingId.value) return;
  
  submitting.value = true;
  try {
    const checks: any[] = [];

    // Iterate all groups (Households)
    groupedHouseholds.value.forEach(hh => {
        // Iterate all spaces in household
        hh.spaces.forEach(space => {
            const unitKey = `${hh.name}_${space.id}`;
            const activeViolations = violations.value[unitKey] || [];
            const isDirty = activeViolations.length > 0;
            
            checks.push({
                room_id: hh.roomId, 
                patrol_location_id: space.id,
                status: isDirty ? 'on' : 'off',
                notes: isDirty ? activeViolations.join(', ') : null,
            });
        });
    });

    const payload = {
      building_id: selectedBuildingId.value,
      checks: checks
    };

    await apiFetch('/api/v1/lights-out/', {
      method: 'POST',
      body: payload
    });

    showSnackbar({ message: t('patrol.patrolSubmitted'), type: 'success' });
    
    setTimeout(() => {
      clearViolations();
      clearSelection();
    }, 1000);

  } catch (err: any) {
    console.error(err);
    showSnackbar({ message: err.message || t('common.error'), type: 'error' });
  } finally {
    submitting.value = false;
  }
};
</script>

<style scoped>
.no-scrollbar::-webkit-scrollbar {
  display: none;
}
.no-scrollbar {
  -ms-overflow-style: none;
  scrollbar-width: none;
}
</style>