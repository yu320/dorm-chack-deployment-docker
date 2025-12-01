import type { Building, PaginatedResponse } from '~/types';
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

export interface BuildingCreate {
  name: string;
}

export interface BuildingUpdate {
  name?: string;
}

export const useBuildings = () => {
  const endpoint = '/api/v1/buildings';
  const { getAll, getById, create, update, remove, loading, error } = useGenericCrud<Building>(endpoint);
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints (like pagination and full-tree)
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n();

  // Expose combined loading and error states
  const isLoading = computed(() => loading.value);

  /**
   * 獲取建築物列表
   */
  const getBuildings = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Building>> => {
    loading.value = true;
    error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      const response = await apiFetch(`${endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Building>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch buildings:', err);
      error.value = err.message || t('snackbar.failedToLoadBuildings');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 獲取單一建築物
   */
  const getBuilding = async (id: number) => {
    try {
      return await getById(String(id));
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToLoadData'), type: 'error' });
      throw err;
    }
  };

  /**
   * 建立建築物
   */
  const createBuilding = async (building: BuildingCreate) => {
    try {
      const newBuilding = await create(building);
      if (newBuilding) {
        showSnackbar({ message: t('snackbar.buildingCreated'), type: 'success' }); // Assuming new i18n key
      }
      return newBuilding;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToSaveBuilding'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  /**
   * 更新建築物
   */
  const updateBuilding = async (id: number, building: BuildingUpdate) => {
    try {
      const updatedBuilding = await update(String(id), building);
      if (updatedBuilding) {
        showSnackbar({ message: t('snackbar.buildingUpdated'), type: 'success' }); // Assuming new i18n key
      }
      return updatedBuilding;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToSaveBuilding'), type: 'error' });
      throw err;
    }
  };

  /**
   * 刪除建築物
   */
  const deleteBuilding = async (id: number) => {
    try {
      const success = await remove(String(id));
      if (success) {
        showSnackbar({ message: t('snackbar.buildingDeleted'), type: 'success' }); // Assuming new i18n key
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToDeleteBuilding'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  /**
   * 獲取包含房間和床位的完整建築物樹狀結構 (保留自定義邏輯)
   */
  const getBuildingsFullTree = async () => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiFetch(`${endpoint}/full-tree/`) as Building[];
      return response;
    } catch (err: any) {
      console.error('Failed to fetch building full tree:', err);
      error.value = err.message || t('snackbar.failedToLoadBuildingData'); // Use generic data load error
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  return {
    isLoading,
    error,
    getBuildings,
    getBuilding,
    createBuilding,
    updateBuilding,
    deleteBuilding,
    getBuildingsFullTree,
  };
};