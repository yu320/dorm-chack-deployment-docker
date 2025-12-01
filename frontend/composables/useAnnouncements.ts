/**
 * Composable for managing announcements
 */
import type { Ref } from 'vue';
import { computed } from 'vue';
import type { Announcement, PaginatedResponse } from '~/types';
import { useGenericCrud } from './useGenericCrud';
import { useSnackbar } from './useSnackbar';
import { useI18n } from '#imports';

export interface AnnouncementCreate {
    title: string;
    content: string;
    tag: string;
    tag_type?: string;
    title_en?: string;
    content_en?: string;
}

export interface AnnouncementUpdate {
    title?: string;
    content?: string;
    tag?: string;
    tag_type?: string;
    is_active?: boolean;
    title_en?: string;
    content_en?: string;
}

export const useAnnouncements = () => {
    const endpoint = '/api/v1/announcements';
    const { getAll, getById, create, update, remove, loading, error } = useGenericCrud<Announcement>(endpoint);
    const { apiFetch } = useAuth(); // Keep apiFetch for custom endpoints (like pagination)
    const { showSnackbar } = useSnackbar();
    const { t } = useI18n();

    // Expose loading and error states
    const isLoading = computed(() => loading.value);

    /**
     * 獲取公告列表
     */
    const getAnnouncements = async (params: Record<string, any> = {}): Promise<PaginatedResponse<Announcement>> => {
        loading.value = true;
        error.value = null;
        try {
            const queryParams = new URLSearchParams();
            Object.entries(params).forEach(([key, value]) => {
                if (value !== null && value !== undefined && value !== '') {
                    queryParams.append(key, String(value));
                }
            });
            const response = await apiFetch(`${endpoint}?${queryParams.toString()}`) as PaginatedResponse<Announcement>;
            return response;
        } catch (err: any) {
            console.error('Failed to fetch announcements:', err);
            error.value = err.message || t('snackbar.failedToLoadAnnouncements'); // Assuming new i18n key
            showSnackbar({ message: error.value, type: 'error' });
            throw err;
        } finally {
            loading.value = false;
        }
    };

    /**
     * 獲取單一公告
     */
    const getAnnouncement = async (id: string) => {
        try {
            return await getById(id);
        } catch (err: any) {
            showSnackbar({ message: error.value || t('snackbar.failedToLoadData'), type: 'error' });
            throw err;
        }
    };

    /**
     * 建立新公告
     */
    const createAnnouncement = async (announcement: AnnouncementCreate) => {
        try {
            const newAnnouncement = await create(announcement);
            if (newAnnouncement) {
                showSnackbar({ message: t('snackbar.announcementCreated'), type: 'success' }); // Assuming new i18n key
            }
            return newAnnouncement;
        } catch (err: any) {
            showSnackbar({ message: error.value || t('snackbar.failedToSaveAnnouncement'), type: 'error' }); // Assuming new i18n key
            throw err;
        }
    };

    /**
     * 更新公告
     */
    const updateAnnouncement = async (id: string, announcement: AnnouncementUpdate) => {
        try {
            const updatedAnnouncement = await update(id, announcement);
            if (updatedAnnouncement) {
                showSnackbar({ message: t('snackbar.announcementUpdated'), type: 'success' }); // Assuming new i18n key
            }
            return updatedAnnouncement;
        } catch (err: any) {
            showSnackbar({ message: error.value || t('snackbar.failedToSaveAnnouncement'), type: 'error' });
            throw err;
        }
    };

    /**
     * 刪除公告
     */
    const deleteAnnouncement = async (id: string) => {
        try {
            const success = await remove(id);
            if (success) {
                showSnackbar({ message: t('snackbar.announcementDeleted'), type: 'success' }); // Assuming new i18n key
            }
            return success;
        } catch (err: any) {
            showSnackbar({ message: error.value || t('snackbar.failedToDeleteAnnouncement'), type: 'error' }); // Assuming new i18n key
            throw err;
        }
    };

    return {
        isLoading,
        error,
        getAnnouncements,
        getAnnouncement,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
    };
};