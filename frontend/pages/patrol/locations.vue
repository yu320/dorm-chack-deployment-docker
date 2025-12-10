<template>
  <div class="container mx-auto px-4 py-8">
    <div class="flex justify-between items-center mb-6">
        <div>
            <h1 class="text-3xl font-bold text-gray-800 dark:text-white">檢查空間設定</h1>
            <p class="text-gray-500 dark:text-gray-400 mt-1">設定各棟建築物的檢查區域，可設定全棟通用或指定特定戶別。</p>
        </div>
    </div>

    <!-- Building Selector -->
    <div class="mb-8 bg-white dark:bg-gray-800 p-4 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700">
      <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-2">選擇建築物</label>
      <select 
        v-model="selectedBuilding" 
        @change="loadLocations"
        class="w-full md:w-1/3 px-4 py-2.5 bg-gray-50 dark:bg-gray-700 border border-gray-200 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none transition-all"
      >
        <option :value="null">請選擇建築物</option>
        <option v-for="building in buildings" :key="building.id" :value="building.id">
          {{ building.name }}
        </option>
      </select>
    </div>

    <!-- Locations List -->
    <div v-if="selectedBuilding" class="bg-white dark:bg-gray-800 rounded-xl shadow-sm border border-gray-100 dark:border-gray-700 overflow-hidden">
      <div class="p-6 border-b border-gray-100 dark:border-gray-700 flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
            <h2 class="text-xl font-bold text-gray-800 dark:text-white">空間列表</h2>
            <p class="text-sm text-gray-500">這些空間將會顯示在對應戶別的檢查清單中</p>
        </div>
        <button 
          @click="openCreateModal"
          class="flex items-center gap-2 bg-primary-600 hover:bg-primary-700 text-white px-5 py-2.5 rounded-lg font-medium transition-colors shadow-sm"
        >
          <Icon name="lucide:plus" class="w-4 h-4" />
          新增空間
        </button>
      </div>

      <div class="p-6">
        <div v-if="loading" class="flex justify-center py-12">
            <Icon name="lucide:loader-2" class="w-8 h-8 animate-spin text-primary-500" />
        </div>
        <div v-else-if="locations.length === 0" class="text-center py-12 text-gray-400 bg-gray-50 dark:bg-gray-800/50 rounded-lg border-2 border-dashed border-gray-200 dark:border-gray-700 m-4">
          <Icon name="lucide:layout-grid" class="w-12 h-12 mx-auto mb-3 opacity-50" />
          <p>尚未設定任何空間</p>
          <p class="text-sm">點擊右上角新增，例如「浴室」、「陽台」</p>
        </div>
        <div v-else class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
          <div 
            v-for="location in locations" 
            :key="location.id"
            class="group relative bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-5 hover:shadow-md transition-all duration-300"
          >
            <div class="flex justify-between items-start mb-3">
                <div>
                    <div class="flex items-center gap-2 flex-wrap">
                        <h3 class="font-bold text-lg text-gray-800 dark:text-white">{{ location.name }}</h3>
                        <div v-if="location.household" class="flex flex-wrap gap-1">
                            <span v-for="h in location.household.split(',')" :key="h" class="px-2 py-0.5 bg-yellow-100 text-yellow-700 text-xs font-bold rounded">
                                {{ h }}
                            </span>
                        </div>
                        <span v-else class="px-2 py-0.5 bg-green-100 text-green-700 text-xs font-bold rounded">
                            全棟通用
                        </span>
                    </div>
                </div>
                
                <div class="flex gap-1 opacity-0 group-hover:opacity-100 transition-opacity">
                    <button @click="editLocation(location)" class="p-2 text-gray-400 hover:text-primary-600 hover:bg-primary-50 rounded-lg transition-colors">
                        <Icon name="lucide:edit-2" class="w-4 h-4" />
                    </button>
                    <button @click="deleteLocation(location.id)" class="p-2 text-gray-400 hover:text-red-600 hover:bg-red-50 rounded-lg transition-colors">
                        <Icon name="lucide:trash-2" class="w-4 h-4" />
                    </button>
                </div>
            </div>

            <!-- Check Items Preview -->
            <div class="flex flex-wrap gap-1.5">
                <span 
                  v-for="(item, idx) in location.check_items" 
                  :key="idx"
                  class="text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 px-2.5 py-1 rounded-md border border-gray-200 dark:border-gray-600"
                >
                  {{ getItemLabel(item) }}
                </span>
                <span v-if="!location.check_items || location.check_items.length === 0" class="text-xs text-gray-400 italic">
                  無檢查項目
                </span>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Create/Edit Modal -->
    <div v-if="showCreateModal" class="fixed inset-0 z-50 overflow-y-auto" aria-labelledby="modal-title" role="dialog" aria-modal="true">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-gray-900/75 backdrop-blur-sm transition-opacity" @click="closeModal"></div>

      <div class="flex min-h-full items-center justify-center p-4 text-center sm:p-0">
        <div class="relative transform rounded-2xl bg-white dark:bg-gray-800 text-left shadow-xl transition-all sm:my-8 sm:w-full sm:max-w-lg border border-gray-100 dark:border-gray-700 flex flex-col max-h-[90vh]">
            
            <!-- Modal Header -->
            <div class="bg-gray-50 dark:bg-gray-900/50 px-6 py-4 border-b border-gray-100 dark:border-gray-700 flex justify-between items-center shrink-0">
                <h3 class="text-lg font-bold text-gray-900 dark:text-white" id="modal-title">
                    {{ editingLocation ? '編輯空間設定' : '新增空間設定' }}
                </h3>
                <button @click="closeModal" class="text-gray-400 hover:text-gray-500">
                    <Icon name="lucide:x" class="w-5 h-5" />
                </button>
            </div>

            <!-- Scrollable Content -->
            <div class="overflow-y-auto px-6 py-6 custom-scrollbar" :class="dropdownPaddingClass">
                <form @submit.prevent="saveLocation" id="location-form" class="space-y-5">
                    
                    <!-- Space Name -->
                    <div>
                        <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5">
                            空間名稱 <span class="text-red-500">*</span>
                        </label>
                        <input 
                            v-model="formData.name"
                            type="text"
                            required
                            placeholder="例如：浴室、陽台、書桌區"
                            class="w-full px-4 py-2.5 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-primary-500 outline-none transition-all"
                        />
                    </div>

                    <!-- Check Items -->
                    <div>
                        <label class="block text-sm font-bold text-gray-700 dark:text-gray-300 mb-1.5">
                            檢查項目
                        </label>
                        
                        <!-- Preset Items Toggles -->
                        <div class="flex flex-wrap gap-2 mb-3">
                            <button
                                v-for="preset in presetItems"
                                :key="preset.name_en"
                                type="button"
                                @click="togglePresetItem(preset)"
                                :class="[
                                    'px-3 py-1.5 rounded-lg text-sm font-medium border transition-all flex items-center gap-1.5',
                                    hasPresetItem(preset)
                                        ? 'bg-primary-50 border-primary-200 text-primary-700 dark:bg-primary-900/30 dark:border-primary-800 dark:text-primary-300'
                                        : 'bg-white border-gray-200 text-gray-600 hover:bg-gray-50 dark:bg-gray-800 dark:border-gray-600 dark:text-gray-400 dark:hover:bg-gray-700'
                                ]"
                            >
                                <Icon :name="hasPresetItem(preset) ? 'lucide:check' : 'lucide:plus'" class="w-3.5 h-3.5" />
                                {{ preset.name_zh }}
                            </button>
                        </div>

                        <div class="bg-gray-50 dark:bg-gray-900/50 p-4 rounded-xl border border-gray-200 dark:border-gray-700">
                            <div class="flex gap-2 mb-3">
                                <input 
                                    v-model="newItemNameZh"
                                    type="text"
                                    placeholder="自訂項目 (中文)"
                                    class="flex-1 min-w-0 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                    @keydown.enter.prevent="focusEnInput"
                                />
                                <input 
                                    ref="enInputRef"
                                    v-model="newItemNameEn"
                                    type="text"
                                    placeholder="英文 (選填)"
                                    class="flex-1 min-w-0 px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-primary-500 outline-none"
                                    @keydown.enter.prevent="addCheckItem"
                                />
                                <button 
                                    type="button"
                                    @click="addCheckItem"
                                    class="px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg transition-colors flex items-center justify-center"
                                >
                                    <Icon name="lucide:plus" class="w-4 h-4" />
                                </button>
                            </div>

                            <!-- Items Tags -->
                            <div class="flex flex-wrap gap-2 min-h-[2rem]">
                                <span v-if="formData.check_items.length === 0" class="text-sm text-gray-400 italic w-full text-center py-2">
                                    請從上方選擇或自行輸入項目
                                </span>
                                <div 
                                    v-for="(item, idx) in formData.check_items" 
                                    :key="idx"
                                    class="flex items-center gap-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 px-3 py-1.5 rounded-lg text-sm shadow-sm group"
                                >
                                    <span class="font-medium text-gray-700 dark:text-gray-200">{{ getItemLabel(item) }}</span>
                                    <button 
                                    type="button" 
                                    @click="removeCheckItem(idx)"
                                    class="text-gray-400 hover:text-red-500 transition-colors"
                                    >
                                    <Icon name="lucide:x" class="w-3.5 h-3.5" />
                                    </button>
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- Advanced Options (Household) -->
                    <div class="pt-2">
                        <div class="relative flex items-start mb-3">
                            <div class="flex h-6 items-center">
                                <input 
                                    id="is-specific" 
                                    type="checkbox" 
                                    v-model="isSpecificHousehold"
                                    class="h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-600"
                                >
                            </div>
                            <div class="ml-3 text-sm leading-6">
                                <label for="is-specific" class="font-medium text-gray-900 dark:text-white">僅限特定戶別使用 (可複選)</label>
                                <p class="text-gray-500 dark:text-gray-400">若勾選，此空間只會出現在指定的戶號中。</p>
                            </div>
                        </div>

                        <!-- Household Multi-Select -->
                        <div v-if="isSpecificHousehold" class="animate-in fade-in slide-in-from-top-2 duration-200 relative">
                            <div class="w-full min-h-[42px] px-2 py-1.5 bg-white dark:bg-gray-900 border border-gray-300 dark:border-gray-600 rounded-lg focus-within:ring-2 focus-within:ring-primary-500 focus-within:border-primary-500 flex flex-wrap gap-1.5"
                                 @click="showHouseholdDropdown = true">
                                
                                <!-- Selected Tags -->
                                <span v-for="h in selectedHouseholds" :key="h" class="inline-flex items-center px-2 py-1 rounded bg-primary-50 dark:bg-primary-900/30 text-primary-700 dark:text-primary-300 text-sm font-medium">
                                    {{ h }}
                                    <button @click.stop="removeHousehold(h)" class="ml-1 text-primary-400 hover:text-primary-600">
                                        <Icon name="lucide:x" class="w-3 h-3" />
                                    </button>
                                </span>

                                <!-- Input for filtering -->
                                <input 
                                    v-model="householdSearch"
                                    type="text"
                                    placeholder="搜尋戶號..."
                                    class="flex-1 min-w-[100px] border-none bg-transparent p-1 focus:ring-0 text-sm outline-none"
                                    @focus="showHouseholdDropdown = true"
                                />
                            </div>

                            <!-- Dropdown Menu -->
                            <div v-if="showHouseholdDropdown" 
                                 class="absolute z-10 mt-1 w-full max-h-60 overflow-auto rounded-md bg-white dark:bg-gray-800 py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm custom-scrollbar border border-gray-100 dark:border-gray-700"
                                 @mouseleave="showHouseholdDropdown = false"
                            >
                                <div v-if="filteredHouseholds.length === 0" class="px-4 py-2 text-gray-500 italic">無符合戶號</div>
                                <button
                                    v-for="h in filteredHouseholds"
                                    :key="h"
                                    type="button"
                                    @click="selectHousehold(h)"
                                    class="w-full text-left relative cursor-default select-none py-2 pl-3 pr-9 hover:bg-primary-50 dark:hover:bg-primary-900/20 text-gray-900 dark:text-gray-200"
                                >
                                    {{ h }}
                                    <span v-if="selectedHouseholds.includes(h)" class="absolute inset-y-0 right-0 flex items-center pr-4 text-primary-600">
                                        <Icon name="lucide:check" class="w-4 h-4" />
                                    </span>
                                </button>
                            </div>
                        </div>
                    </div>
                </form>
            </div>

            <!-- Modal Footer -->
            <div class="bg-gray-50 dark:bg-gray-900/50 px-6 py-4 border-t border-gray-100 dark:border-gray-700 flex justify-end gap-3 shrink-0 rounded-b-2xl">
                <button 
                    type="button"
                    @click="closeModal"
                    class="px-5 py-2.5 bg-white dark:bg-gray-800 border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-200 font-medium rounded-xl hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors focus:ring-2 focus:ring-offset-2 focus:ring-gray-200"
                >
                    取消
                </button>
                <button 
                    type="submit"
                    form="location-form"
                    class="px-5 py-2.5 bg-primary-600 text-white font-bold rounded-xl hover:bg-primary-700 transition-colors shadow-lg shadow-primary-500/30 focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
                >
                    確認儲存
                </button>
            </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch, nextTick } from 'vue';
import { useAuth } from '~/composables/useAuth';
import { useSnackbar } from '~/composables/useSnackbar';
import { useRooms } from '~/composables/useRooms';

const { apiFetch } = useAuth();
const { showSnackbar } = useSnackbar();
const { getRooms } = useRooms();

const buildings = ref([]);
const selectedBuilding = ref(null);
const locations = ref([]);
const rooms = ref([]);
const loading = ref(false);
const showCreateModal = ref(false);
const editingLocation = ref(null);

interface CheckItem {
    name_zh: string;
    name_en: string;
}

const formData = ref({
  name: '',
  household: '', // Stores comma-separated string
  building_id: null,
  check_items: [] as (string | CheckItem)[]
});

// Preset Items
const presetItems: CheckItem[] = [
    { name_zh: '電燈', name_en: 'Light' },
    { name_zh: '冷氣', name_en: 'AC' },
    { name_zh: '門窗', name_en: 'Door/Window' },
    { name_zh: '風扇', name_en: 'Fan' },
    { name_zh: '插座', name_en: 'Socket' }
];

const isSpecificHousehold = ref(false);

// New States for Multi-Select
const selectedHouseholds = ref<string[]>([]);
const householdSearch = ref('');
const showHouseholdDropdown = ref(false);

const newItemNameZh = ref('');
const newItemNameEn = ref('');
const enInputRef = ref(null);

const availableHouseholds = computed(() => {
    if (!rooms.value.length) return [];
    const households = rooms.value.map(r => r.household).filter(h => h && h.trim() !== '');
    return [...new Set(households)].sort();
});

const filteredHouseholds = computed(() => {
    const term = householdSearch.value.toLowerCase();
    return availableHouseholds.value.filter(h => 
        h.toLowerCase().includes(term) && !selectedHouseholds.value.includes(h)
    );
});

// Computed for dynamic padding class
const dropdownPaddingClass = computed(() => {
    return showHouseholdDropdown.value ? 'pb-60' : ''; // Adjust padding to leave space for dropdown
});


// Watch toggle to clear selection
watch(isSpecificHousehold, (val) => {
    if (!val) {
        selectedHouseholds.value = [];
        formData.value.household = '';
    }
});

onMounted(async () => {
  try {
    const response = await apiFetch('/api/v1/buildings/');
    buildings.value = response;
  } catch (error) {
    showSnackbar({ message: '載入建築物列表失敗', type: 'error' });
  }
});

async function loadLocations() {
  if (!selectedBuilding.value) return;
  
  loading.value = true;
  try {
    const locResponse = await apiFetch(`/api/v1/patrol-locations/?building_id=${selectedBuilding.value}`);
    locations.value = locResponse.records || [];

    const roomsResponse = await getRooms({ building_id: selectedBuilding.value, limit: 2000 });
    rooms.value = roomsResponse.records || [];

  } catch (error) {
    showSnackbar({ message: '載入資料失敗', type: 'error' });
  } finally {
    loading.value = false;
  }
}

function openCreateModal() {
    editingLocation.value = null;
    formData.value = { name: '', household: '', building_id: null, check_items: [] };
    isSpecificHousehold.value = false;
    selectedHouseholds.value = [];
    showCreateModal.value = true;
    householdSearch.value = '';
    nextTick(() => { // Ensure dropdown is not immediately hidden if it was open from previous edit
        showHouseholdDropdown.value = false;
    });
}

function editLocation(location) {
  editingLocation.value = location;
  formData.value = {
    name: location.name,
    household: location.household || '',
    building_id: location.building_id,
    check_items: location.check_items ? JSON.parse(JSON.stringify(location.check_items)) : []
  };
  
  // Parse CSV household string to array
  if (location.household) {
      isSpecificHousehold.value = true;
      selectedHouseholds.value = location.household.split(',').map(s => s.trim()).filter(s => s);
  } else {
      isSpecificHousehold.value = false;
      selectedHouseholds.value = [];
  }
  
  showCreateModal.value = true;
  householdSearch.value = '';
  nextTick(() => {
      showHouseholdDropdown.value = false; // Ensure dropdown is closed initially
  });
}

function closeModal() {
  showCreateModal.value = false;
  editingLocation.value = null;
  newItemNameZh.value = '';
  newItemNameEn.value = '';
  householdSearch.value = '';
  showHouseholdDropdown.value = false; // Ensure it's closed
}

// Preset Logic
function hasPresetItem(preset: CheckItem) {
    return formData.value.check_items.some(item => {
        if (typeof item === 'string') return item === preset.name_zh;
        return item.name_zh === preset.name_zh;
    });
}

function togglePresetItem(preset: CheckItem) {
    if (hasPresetItem(preset)) {
        // Remove
        formData.value.check_items = formData.value.check_items.filter(item => {
            if (typeof item === 'string') return item !== preset.name_zh;
            return item.name_zh !== preset.name_zh;
        });
    } else {
        // Add
        formData.value.check_items.push({ ...preset });
    }
}

// Multi-Select Logic
function selectHousehold(h: string) {
    if (!selectedHouseholds.value.includes(h)) {
        selectedHouseholds.value.push(h);
    }
    householdSearch.value = ''; // Clear search
    // Keep dropdown open for multi-select convenience? Or close it?
    // Let's keep it open but focus input
}

function removeHousehold(h: string) {
    selectedHouseholds.value = selectedHouseholds.value.filter(item => item !== h);
}

function focusEnInput() {
    enInputRef.value?.focus();
}

function addCheckItem() {
  const zh = newItemNameZh.value.trim();
  const en = newItemNameEn.value.trim();
  
  if (!zh) return;

  const newItem = { name_zh: zh, name_en: en || zh };
  formData.value.check_items.push(newItem);
  
  newItemNameZh.value = '';
  newItemNameEn.value = '';
}

function removeCheckItem(index: number) {
  formData.value.check_items.splice(index, 1);
}

function getItemLabel(item: string | CheckItem): string {
    if (typeof item === 'string') return item;
    return `${item.name_zh} ${item.name_en !== item.name_zh ? '(' + item.name_en + ')' : ''}`;
}

async function saveLocation() {
  formData.value.building_id = selectedBuilding.value;
  
  // Combine selected households into CSV string
  if (isSpecificHousehold.value && selectedHouseholds.value.length > 0) {
      formData.value.household = selectedHouseholds.value.join(',');
  } else {
      formData.value.household = null;
  }
  
  try {
    if (editingLocation.value) {
      await apiFetch(`/api/v1/patrol-locations/${editingLocation.value.id}`, {
        method: 'PUT',
        body: formData.value
      });
      showSnackbar({ message: '設定更新成功', type: 'success' });
    } else {
      await apiFetch('/api/v1/patrol-locations/', {
        method: 'POST',
        body: formData.value
      });
      showSnackbar({ message: '設定新增成功', type: 'success' });
    }
    closeModal();
    loadLocations();
  } catch (error) {
    showSnackbar({ message: '儲存失敗', type: 'error' });
  }
}

async function deleteLocation(id) {
  if (!confirm('確定要刪除此設定嗎？')) return;
  
  try {
    await apiFetch(`/api/v1/patrol-locations/${id}`, { method: 'DELETE' });
    showSnackbar({ message: '刪除成功', type: 'success' });
    loadLocations();
  } catch (error) {
    showSnackbar({ message: '刪除失敗', type: 'error' });
  }
}
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #e5e7eb;
  border-radius: 20px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #374151;
}
</style>