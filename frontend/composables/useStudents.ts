import type { Student, PaginatedResponse } from '~/types'
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useI18n } from '#imports'; // Import useI18n

export interface StudentCreate {
  student_id_number: string
  full_name: string
  class_name?: string
  gender?: string
  identity_status?: string
  is_foreign_student?: boolean
  enrollment_status?: string
  remarks?: string
  license_plate?: string
  contract_info?: string
  temp_card_number?: string
  bed_id?: number | null
}

export interface StudentUpdate {
  student_id_number?: string
  full_name?: string
  class_name?: string
  gender?: string
  identity_status?: string
  is_foreign_student?: boolean
  enrollment_status?: string
  remarks?: string
  license_plate?: string
  contract_info?: string
  temp_card_number?: string
  bed_id?: number | null
}

export interface StudentAssignBed {
  bed_id: number | null
}

export const useStudents = () => {
  const endpoint = '/api/v1/students';
  const { getAll, getById, create, update, remove, loading, error } = useGenericCrud<Student>(endpoint);
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n(); // Initialize useI18n

  /**
   * 獲取學生列表 (使用泛型 CRUD)
   */
  const getStudents = async (params: Record<string, any> = {}) => {
    try {
      // The generic getAll returns T[], but our API returns PaginatedResponse<Student>
      // We need to either adjust useGenericCrud to handle pagination,
      // or keep this wrapper. For now, keeping wrapper for pagination.
      loading.value = true;
      error.value = null;
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      
      const response = await apiFetch(`${endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Student>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch students:', err);
      error.value = err.message || 'Failed to fetch students';
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 獲取單一學生 (使用泛型 CRUD)
   */
  const getStudent = async (id: string) => {
    try {
      return await getById(id);
    } catch (err: any) {
      showSnackbar({ message: error.value || 'Failed to fetch student', type: 'error' });
      throw err;
    }
  };

  /**
   * 建立學生 (使用泛型 CRUD)
   */
     const createStudent = async (student: StudentCreate) => {
      try {
        const newStudent = await create(student);
        if (newStudent) {
          showSnackbar({ message: t('snackbar.studentCreated'), type: 'success' });
        }
        return newStudent;
      } catch (err: any) {
        showSnackbar({ message: error.value || t('snackbar.failedToSaveStudent'), type: 'error' });
        throw err;
      }
    };
  /**
   * 更新學生資料 (使用泛型 CRUD)
   */
     const updateStudent = async (id: string, student: StudentUpdate) => {
      try {
        const updatedStudent = await update(id, student);
        if (updatedStudent) {
          showSnackbar({ message: t('snackbar.studentUpdated'), type: 'success' });
        }
        return updatedStudent;
      } catch (err: any) {
        showSnackbar({ message: error.value || t('snackbar.failedToSaveStudent'), type: 'error' });
        throw err;
      }
    };
  /**
   * 分配床位 (保持自定義邏輯)
   */
  const assignBed = async (studentId: string, bedId: number | null) => {
    loading.value = true;
    error.value = null;
    try {
      const response = await apiFetch(`${endpoint}/${studentId}/assign-bed`, {
        method: 'PUT',
        body: { bed_id: bedId },
      }) as Student;
      if (response) {
        showSnackbar({ message: t('snackbar.assignBedSuccess'), type: 'success' }); // Assuming a new i18n key for assign bed success
      }
      return response;
    } catch (err: any) {
      console.error('Failed to assign bed:', err);
      error.value = err.message || t('snackbar.failedToAssignBed'); // Assuming a new i18n key for assign bed failure
      showSnackbar({ message: error.value, type: 'error' });
      throw err;
    } finally {
      loading.value = false;
    }
  };

  /**
   * 刪除學生 (使用泛型 CRUD)
   */
     const deleteStudent = async (id: string) => {
      try {
        const success = await remove(id);
        if (success) {
          showSnackbar({ message: t('snackbar.studentDeleted'), type: 'success' });
        }
        return success;
      } catch (err: any) {
        showSnackbar({ message: error.value || t('snackbar.failedToDeleteStudent'), type: 'error' });
        throw err;
      }
    };
  // Expose combined loading and error states
  const isLoading = computed(() => loading.value);

  return {
    isLoading, // Export isLoading instead of loading
    error,   // Use error from generic composable
    getStudents,
    getStudent,
    createStudent,
    updateStudent,
    assignBed,
    deleteStudent,
  };
};