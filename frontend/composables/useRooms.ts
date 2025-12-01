import type { Room, Bed, PaginatedResponse } from '~/types';
import { computed } from 'vue';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

export interface RoomCreate {
  building_id: number;
  room_number: string;
  household?: string;
  room_type?: string;
}

export interface RoomUpdate {
  building_id?: number;
  room_number?: string;
  household?: string;
  room_type?: string;
}

export interface BedCreate {
  room_id: number;
  bed_number: string;
  bed_type?: string;
  status?: string;
}

export interface BedUpdate {
  room_id?: number;
  bed_number?: string;
  bed_type?: string;
  status?: string;
}

export const useRooms = () => {
  const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints
  const { showSnackbar } = useSnackbar();
  const { t } = useI18n();

  // --- Room Operations ---
  const roomsCrud = useGenericCrud<Room>('/api/v1/rooms');
  const bedsCrud = useGenericCrud<Bed>('/api/v1/beds');

  // Expose loading and error states, decide which one to prioritize or combine
  const isLoading = computed(() => roomsCrud.loading.value || bedsCrud.loading.value);
  const error = computed(() => roomsCrud.error.value || bedsCrud.error.value);


  const getRooms = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Room>> => {
    roomsCrud.loading.value = true;
    roomsCrud.error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      // Directly using apiFetch for pagination handling for now, similar to useStudents
      const response = await apiFetch(`${roomsCrud.endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Room>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch rooms:', err);
      roomsCrud.error.value = err.message || t('snackbar.failedToLoadRooms');
      showSnackbar({ message: roomsCrud.error.value, type: 'error' });
      throw err;
    } finally {
      roomsCrud.loading.value = false;
    }
  };

  const getRoom = async (id: number): Promise<Room | null> => {
    try {
      return await roomsCrud.getById(String(id)); // GenericCrud takes string ID
    } catch (err: any) {
      showSnackbar({ message: roomsCrud.error.value || t('snackbar.failedToLoadData'), type: 'error' });
      throw err;
    }
  };

  const createRoom = async (room: RoomCreate): Promise<Room | null> => {
    try {
      const newRoom = await roomsCrud.create(room);
      if (newRoom) {
        showSnackbar({ message: t('snackbar.roomCreated'), type: 'success' }); // Assuming new i18n key
      }
      return newRoom;
    } catch (err: any) {
      showSnackbar({ message: roomsCrud.error.value || t('snackbar.failedToSaveRoom'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  const updateRoom = async (id: number, room: RoomUpdate): Promise<Room | null> => {
    try {
      const updatedRoom = await roomsCrud.update(String(id), room);
      if (updatedRoom) {
        showSnackbar({ message: t('snackbar.roomUpdated'), type: 'success' }); // Assuming new i18n key
      }
      return updatedRoom;
    } catch (err: any) {
      showSnackbar({ message: roomsCrud.error.value || t('snackbar.failedToSaveRoom'), type: 'error' });
      throw err;
    }
  };

  const deleteRoom = async (id: number): Promise<boolean> => {
    try {
      const success = await roomsCrud.remove(String(id));
      if (success) {
        showSnackbar({ message: t('snackbar.roomDeleted'), type: 'success' }); // Assuming new i18n key
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: roomsCrud.error.value || t('snackbar.failedToDeleteRoom'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  // --- Bed Operations ---

  const getBeds = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Bed>> => {
    bedsCrud.loading.value = true;
    bedsCrud.error.value = null;
    try {
      const queryParams = new URLSearchParams();
      Object.entries(params).forEach(([key, value]) => {
        if (value !== null && value !== undefined && value !== '') {
          queryParams.append(key, String(value));
        }
      });
      const response = await apiFetch(`${bedsCrud.endpoint}/?${queryParams.toString()}`) as PaginatedResponse<Bed>;
      return response;
    } catch (err: any) {
      console.error('Failed to fetch beds:', err);
      bedsCrud.error.value = err.message || t('snackbar.failedToLoadBeds'); // Assuming new i18n key
      showSnackbar({ message: bedsCrud.error.value, type: 'error' });
      throw err;
    } finally {
      bedsCrud.loading.value = false;
    }
  };

  const getBed = async (id: number): Promise<Bed | null> => {
    try {
      return await bedsCrud.getById(String(id));
    } catch (err: any) {
      showSnackbar({ message: bedsCrud.error.value || t('snackbar.failedToLoadData'), type: 'error' });
      throw err;
    }
  };

  const createBed = async (bed: BedCreate): Promise<Bed | null> => {
    try {
      const newBed = await bedsCrud.create(bed);
      if (newBed) {
        showSnackbar({ message: t('snackbar.bedCreated'), type: 'success' }); // Assuming new i18n key
      }
      return newBed;
    } catch (err: any) {
      showSnackbar({ message: bedsCrud.error.value || t('snackbar.failedToSaveBed'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };

  const updateBed = async (id: number, bed: BedUpdate): Promise<Bed | null> => {
    try {
      const updatedBed = await bedsCrud.update(String(id), bed);
      if (updatedBed) {
        showSnackbar({ message: t('snackbar.bedUpdated'), type: 'success' }); // Assuming new i18n key
      }
      return updatedBed;
    } catch (err: any) {
      showSnackbar({ message: bedsCrud.error.value || t('snackbar.failedToSaveBed'), type: 'error' });
      throw err;
    }
  };

  const deleteBed = async (id: number): Promise<boolean> => {
    try {
      const success = await bedsCrud.remove(String(id));
      if (success) {
        showSnackbar({ message: t('snackbar.bedDeleted'), type: 'success' }); // Assuming new i18n key
      }
      return success;
    } catch (err: any) {
      showSnackbar({ message: bedsCrud.error.value || t('snackbar.failedToDeleteBed'), type: 'error' }); // Assuming new i18n key
      throw err;
    }
  };


  return {
    isLoading,
    error,
    getRooms,
    getRoom,
    createRoom,
    updateRoom,
    deleteRoom,
    getBeds,
    getBed,
    createBed,
    updateBed,
    deleteBed,
  };
};