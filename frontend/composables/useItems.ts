import type { InspectionItem, PaginatedResponse } from '~/types';
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

export interface InspectionItemCreate {
  name: string;
  name_en?: string;
  description?: string;
  description_en?: string;
}

export interface InspectionItemUpdate {
  name?: string;
  name_en?: string;
  description?: string;
  description_en?: string;
  is_active?: boolean;
}

export const useItems = () => {
  const endpoint = '/api/v1/items';
  const { getAll, getById, create, update, remove, loading, error } = useGenericCrud<InspectionItem>(endpoint);
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n();

  // Expose loading and error states, decide which one to prioritize or combine
  const isLoading = computed(() => loading.value);


  /**
   * 獲取檢查項目列表
   */
  const getItems = async (params: Record<string, any> = {}): Promise<PaginatedResponse<InspectionItem>> => {
    loading.value = true;
    error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      // Directly using apiFetch for pagination handling for now
      const response = await apiFetch(`${endpoint}/?${queryParams.toString()}`) as PaginatedResponse<InspectionItem>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch items:', err);
      error.value = err.message || t('snackbar.failedToLoadItems');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 獲取單一檢查項目
   */
  const getItem = async (id: string) => {
    try {
      return await getById(id);
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToLoadData'), type: 'error' });
      throw err;
    }
  };

  /**
   * 建立檢查項目
   */
  const createItem = async (item: InspectionItemCreate) => {
    try {
      const newItem = await create(item);
      if (newItem) {
        showSnackbar({ message: t('snackbar.itemCreated'), type: 'success' });
      }
      return newItem;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToSaveItem'), type: 'error' });
      throw err;
    }
  };

  /**
   * 更新檢查項目
   */
  const updateItem = async (id: string, item: InspectionItemUpdate) => {
    try {
      const updatedItem = await update(id, item);
      if (updatedItem) {
        showSnackbar({ message: t('snackbar.itemUpdated'), type: 'success' });
      }
      return updatedItem;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToSaveItem'), type: 'error' });
      throw err;
    }
  };

  /**
   * 刪除檢查項目
   */
  const deleteItem = async (id: string) => {
    try {
      const success = await remove(id);
      if (success) {
        showSnackbar({ message: t('snackbar.itemDeleted'), type: 'success' });
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToDeleteItem'), type: 'error' });
      throw err;
    }
  };

  /**
   * 批次更新狀態 (保持自定義邏輯)
   */
  const batchUpdateStatus = async (itemIds: string[], isActive: boolean) => {
      loading.value = true;
      error.value = null;
      try {
          const response = await apiFetch(`${endpoint}/batch-update-status`, {
              method: 'PUT',
              body: {
                  item_ids: itemIds,
                  is_active: isActive
              }
          }) as InspectionItem[];
          if (response) {
            showSnackbar({ message: t('snackbar.batchUpdateItemStatusSuccess'), type: 'success' });
          }
          return response;
      } catch (err: any) {
          console.error('Failed to batch update item status:', err);
          error.value = err.message || t('snackbar.batchUpdateItemStatusFailed');
          showSnackbar({ message: error.value, type: 'error' });
          throw err;
      } finally {
          loading.value = false;
      }
  };

  return {
    isLoading, // Use loading from generic composable
    error,   // Use error from generic composable
    getItems,
    getItem,
    createItem,
    updateItem,
    deleteItem,
    batchUpdateStatus,
  };
};