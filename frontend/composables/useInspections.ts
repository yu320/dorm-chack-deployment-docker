import type { InspectionRecord, PaginatedResponse, InspectionStatus } from '~/types';
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

export interface InspectionCreate {
  student_id?: string;
  room_id?: number;
  details: {
    item_id: string;
    status: string;
    comment?: string;
    photos?: { file_content: string; file_name: string }[];
  }[];
  signature_base64?: string;
}

export interface InspectionRecordUpdate {
  status?: InspectionStatus;
}

export interface SearchParams {
  student_name?: string;
  room_number?: string;
  start_date?: string;
  end_date?: string;
  status?: string;
  skip?: number;
  limit?: number;
}

export const useInspections = () => {
  const endpoint = '/api/v1/inspections';
  const { getAll, getById, create, update, remove, loading, error } = useGenericCrud<InspectionRecord>(endpoint);
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n();

  // Expose loading and error states
  const isLoading = computed(() => loading.value);

  /**
   * 獲取檢查紀錄列表
   */
  const getInspections = async (params: Record<string, any> = {}): Promise<PaginatedResponse<InspectionRecord>> => {
    loading.value = true;
    error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      const response = await apiFetch(`${endpoint}/?${queryParams.toString()}`) as PaginatedResponse<InspectionRecord>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch inspections:', err);
      error.value = err.message || t('snackbar.failedToLoadInspections');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 搜尋檢查紀錄 (保留自定義邏輯)
   */
  const searchInspections = async (params: SearchParams): Promise<PaginatedResponse<InspectionRecord>> => {
    loading.value = true;
    error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      const response = await apiFetch(`${endpoint}/search?${queryParams.toString()}`) as PaginatedResponse<InspectionRecord>;
      return response;
    } catch (err: any) {
      console.error('Failed to search inspections:', err);
      error.value = err.message || t('snackbar.failedToFetchRecords');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 獲取單一檢查紀錄
   */
  const getInspection = async (id: string) => {
    try {
      return await getById(id);
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToLoadRecord'), type: 'error' });
      throw err;
    }
  };

  /**
   * 建立檢查紀錄
   */
  const createInspection = async (inspection: InspectionCreate) => {
    try {
      const newInspection = await create(inspection);
      if (newInspection) {
        showSnackbar({ message: t('snackbar.inspectionSubmitted'), type: 'success' }); // Assuming this is for submission
      }
      return newInspection;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToSubmitInspection'), type: 'error' });
      throw err;
    }
  };

  /**
   * 更新檢查紀錄狀態 (保留自定義邏輯)
   */
  const updateInspectionStatus = async (id: string, newStatus: InspectionStatus) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiFetch(`${endpoint}/${id}`, {
        method: 'PUT',
        body: { status: newStatus },
      }) as InspectionRecord;
      if (response) {
        showSnackbar({ message: t('snackbar.statusUpdated'), type: 'success' });
      }
      return response;
    } catch (err: any) {
      console.error('Failed to update inspection status:', err);
      error.value = err.message || t('snackbar.failedToUpdateStatus');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 發送 Email 報告 (保留自定義邏輯)
   */
  const emailReport = async (id: string, recipientEmail: string) => {
    loading.value = true;
    error.value = null;
    try {
      if (!recipientEmail) {
        throw new Error(t('snackbar.enterRecipientEmail'));
      }
      await apiFetch(`${endpoint}/${id}/email`, {
        method: 'POST',
        body: { recipient_email: recipientEmail },
      });
      showSnackbar({ message: t('snackbar.reportEmailed'), type: 'success' });
      return true;
    } catch (err: any) {
      console.error('Failed to email report:', err);
      error.value = err.message || t('snackbar.failedToEmailReport');
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 刪除檢查紀錄
   */
  const deleteInspection = async (id: string) => {
    try {
      const success = await remove(id);
      if (success) {
        showSnackbar({ message: t('snackbar.recordDeleted'), type: 'success' });
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: error.value || t('snackbar.failedToDeleteRecord'), type: 'error' });
      throw err;
    }
  };

  return {
    isLoading,
    error,
    getInspections,
    searchInspections,
    getInspection,
    createInspection,
    updateInspectionStatus,
    emailReport,
    deleteInspection,
  };
};