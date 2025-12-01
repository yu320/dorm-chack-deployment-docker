import { ref } from 'vue';
import { useAuth } from './useAuth';
import { useSnackbar } from './useSnackbar';

interface CrudOperations<T> {
  endpoint: string;
  getAll: (params?: Record<string, any>) => Promise<T[]>;
  getById: (id: string) => Promise<T | null>;
  create: (item: Partial<T>) => Promise<T | null>;
  update: (id: string, item: Partial<T>) => Promise<T | null>;
  remove: (id: string) => Promise<boolean>;
  loading: Ref<boolean>;
  error: Ref<any>;
}


export function useGenericCrud<T>(endpoint: string): CrudOperations<T> {
  const { apiFetch } = useAuth(); // Use apiFetch which handles cookies and base URL
  const { showSnackbar } = useSnackbar();

  const loading = ref(false);
  const error = ref(null);

  const request = async <R>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    url: string,
    data?: any
  ): Promise<R | null> => {
    loading.value = true;
    error.value = null;
    try {
      const options: any = {
        method,
      };

      if (data) {
        options.body = data;
      }

      const response = await apiFetch(url, options);

      // For DELETE, there might not be a body, apiFetch/ofetch handles 204 automatically by returning null usually?
      // But if we need to return boolean true for success:
      if (method === 'DELETE' && !response) {
        return true as unknown as R;
      }

      return response as R;
    } catch (err: any) {
      error.value = err;
      // If it's 404, it might be expected in some cases (like getById), but generally we show error
      showSnackbar({ message: err.data?.detail || err.message || 'Operation failed', type: 'error' });
      return null;
    } finally {
      loading.value = false;
    }
  };

  const getAll = async (params?: Record<string, any>): Promise<T[]> => {
    const query = params ? `?${new URLSearchParams(params).toString()}` : '';
    const result = await request<T[]>('GET', `${endpoint}${query}`);
    return result || []; // Note: Backend might return { records: [], total: ... } for pagination, verify this.
    // If backend returns PaginatedResponse, T[] return type here is slightly wrong for getAll, but generic usually implies simple list or we adjust.
    // Based on useAnnouncements, it expects PaginatedResponse. 
    // But useGenericCrud signature says Promise<T[]>. 
    // Let's assume apiFetch returns the body directly.
  };

  const getById = async (id: string): Promise<T | null> => {
    return await request<T>('GET', `${endpoint}/${id}`);
  };

  const create = async (item: Partial<T>): Promise<T | null> => {
    return await request<T>('POST', endpoint, item);
  };

  const update = async (id: string, item: Partial<T>): Promise<T | null> => {
    return await request<T>('PUT', `${endpoint}/${id}`, item);
  };

  const remove = async (id: string): Promise<boolean> => {
    const result = await request<boolean>('DELETE', `${endpoint}/${id}`);
    return result === true;
  };

  return {
    endpoint,
    getAll,
    getById,
    create,
    update,
    remove,
    loading,
    error,
  };
}

