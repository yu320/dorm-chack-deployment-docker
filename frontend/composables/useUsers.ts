import type { User, Role, Permission, PaginatedResponse } from '~/types';
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

// User Schemas
export interface UserCreate {
  username: string;
  password?: string;
  email: string;
  student_id_number: string;
  bed_number?: string | null;
}

export interface UserUpdate {
  username?: string;
  email?: string;
  roles?: string[]; // List of Role IDs
  is_active?: boolean;
}

// Role Schemas
export interface RoleCreate {
  name: string;
  permissions: string[]; // List of Permission IDs
}

export interface RoleUpdate {
  name?: string;
  permissions?: string[]; // List of Permission IDs
}

export const useUsers = () => {
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints (like pagination)
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n();

  // --- User Operations ---
  const usersCrud = useGenericCrud<User>('/api/v1/users');
  // --- Role Operations ---
  const rolesCrud = useGenericCrud<Role>('/api/v1/roles');
  // --- Permission Operations ---
  const permissionsCrud = useGenericCrud<Permission>('/api/v1/permissions');

  // Expose combined loading and error states
  const isLoading = computed(() => usersCrud.loading.value || rolesCrud.loading.value || permissionsCrud.loading.value);
  const error = computed(() => usersCrud.error.value || rolesCrud.error.value || permissionsCrud.error.value);

  // --- User-specific functions ---
  const getUsers = async (params: Record<string, any> = {}): Promise<PaginatedResponse<User>> => {
    usersCrud.loading.value = true;
    usersCrud.error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      // Add trailing slash to avoid 307 redirect from backend which causes CORS/Proxy issues
      const response = await apiFetch(`${usersCrud.endpoint}/?${queryParams.toString()}`) as PaginatedResponse<User>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch users:', err);
      usersCrud.error.value = err.message || t('snackbar.failedToLoadUsers');
      showSnackbar({ message: usersCrud.error.value, type: 'error' });
      // Return empty response instead of throwing
      return { total: 0, records: [] };
    } finally {
      usersCrud.loading.value = false;
    }
  };

  const createUser = async (user: UserCreate): Promise<User | null> => {
    try {
      const newUser = await usersCrud.create(user);
      if (newUser) {
        showSnackbar({ message: t('snackbar.userCreated'), type: 'success' }); // Assuming new i18n key
      }
      return newUser;
    } catch (err: any) {
      showSnackbar({ message: usersCrud.error.value || t('snackbar.failedToSaveUser'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  const updateUser = async (id: string, user: UserUpdate): Promise<User | null> => {
    try {
      const updatedUser = await usersCrud.update(id, user);
      if (updatedUser) {
        showSnackbar({ message: t('snackbar.userUpdated'), type: 'success' }); // Assuming new i18n key
      }
      return updatedUser;
    } catch (err: any) {
      showSnackbar({ message: usersCrud.error.value || t('snackbar.failedToSaveUser'), type: 'error' });
      throw err;
    }
  };

  // --- Role-specific functions ---
  const getRoles = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Role>> => {
    rolesCrud.loading.value = true;
    rolesCrud.error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      console.log('Fetching roles with params:', params); // Debug log
      // Add trailing slash to avoid 307 redirect
      const response = await apiFetch(`${rolesCrud.endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Role>;
      console.log('Roles API response:', response); // Debug log
      return response;
    } catch (err: any) {
      console.error('Failed to fetch roles in useUsers:', err); // More specific log
      rolesCrud.error.value = err.message || t('snackbar.failedToLoadRoles');
      showSnackbar({ message: rolesCrud.error.value, type: 'error' });
      // Return empty response instead of throwing
      return { total: 0, records: [] };
    } finally {
      rolesCrud.loading.value = false;
    }
  };

  const createRole = async (role: RoleCreate): Promise<Role | null> => {
    try {
      const newRole = await rolesCrud.create(role);
      if (newRole) {
        showSnackbar({ message: t('snackbar.roleCreated'), type: 'success' }); // Assuming new i18n key
      }
      return newRole;
    } catch (err: any) {
      showSnackbar({ message: rolesCrud.error.value || t('snackbar.failedToSaveRole'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  const updateRole = async (id: string, role: RoleUpdate): Promise<Role | null> => {
    try {
      const updatedRole = await rolesCrud.update(id, role);
      if (updatedRole) {
        showSnackbar({ message: t('snackbar.roleUpdated'), type: 'success' }); // Assuming new i18n key
      }
      return updatedRole;
    } catch (err: any) {
      showSnackbar({ message: rolesCrud.error.value || t('snackbar.failedToSaveRole'), type: 'error' });
      throw err;
    }
  };

  const deleteRole = async (id: string): Promise<boolean> => {
    try {
      const success = await rolesCrud.remove(id);
      if (success) {
        showSnackbar({ message: t('snackbar.roleDeleted'), type: 'success' }); // Assuming new i18n key
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: rolesCrud.error.value || t('snackbar.failedToDeleteRole'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  // --- Permission-specific functions ---
  const getPermissions = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Permission>> => {
    permissionsCrud.loading.value = true;
    permissionsCrud.error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      // Add trailing slash to avoid 307 redirect
      const response = await apiFetch(`${permissionsCrud.endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Permission>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch permissions:', err);
      permissionsCrud.error.value = err.message || t('snackbar.failedToLoadPermissions');
      showSnackbar({ message: permissionsCrud.error.value, type: 'error' });
      // Return empty response instead of throwing
      return { total: 0, records: [] };
    } finally {
      permissionsCrud.loading.value = false;
    }
  };


  return {
    isLoading,
    error,
    getUsers,
    createUser,
    updateUser,
    getRoles,
    createRole,
    updateRole,
    deleteRole,
    getPermissions,
  };
};