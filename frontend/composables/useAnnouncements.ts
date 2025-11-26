/**
 * Composable for managing announcements
 */
import type { Ref } from 'vue'

export interface Announcement {
    id: string
    title: string
    content: string
    tag: string
    tag_type: 'primary' | 'success' | 'warning' | 'danger' | 'info'
    is_active: boolean
    created_at: string
    updated_at: string
}

export interface AnnouncementCreate {
    title: string
    content: string
    tag: string
    tag_type?: string
}

export interface AnnouncementUpdate {
    title?: string
    content?: string
    tag?: string
    tag_type?: string
    is_active?: boolean
}

export const useAnnouncements = () => {
    const config = useRuntimeConfig()
    const { apiFetch } = useAuth()

    /**
     * 獲取公告列表（公開）
     */
    const getAnnouncements = async (skip: number = 0, limit: number = 10) => {
        try {
            const response = await $fetch<{ total: number; records: Announcement[] }>(
                `/api/v1/announcements?skip=${skip}&limit=${limit}`,
                {
                    baseURL: config.public.apiBase,
                    method: 'GET',
                }
            )
            return response
        } catch (error) {
            console.error('Failed to fetch announcements:', error)
            throw error
        }
    }

    /**
     * 獲取單一公告（公開）
     */
    const getAnnouncement = async (id: string) => {
        try {
            const response = await $fetch<Announcement>(
                `/api/v1/announcements/${id}`,
                {
                    baseURL: config.public.apiBase,
                    method: 'GET',
                }
            )
            return response
        } catch (error) {
            console.error('Failed to fetch announcement:', error)
            throw error
        }
    }

    /**
     * 建立新公告（需要管理員權限）
     */
    const createAnnouncement = async (announcement: AnnouncementCreate) => {
        try {
            const response = await apiFetch('/api/v1/announcements', {
                method: 'POST',
                body: announcement,
            })
            return response as Announcement
        } catch (error) {
            console.error('Failed to create announcement:', error)
            throw error
        }
    }

    /**
     * 更新公告（需要管理員權限）
     */
    const updateAnnouncement = async (id: string, announcement: AnnouncementUpdate) => {
        try {
            const response = await apiFetch(`/api/v1/announcements/${id}`, {
                method: 'PUT',
                body: announcement,
            })
            return response as Announcement
        } catch (error) {
            console.error('Failed to update announcement:', error)
            throw error
        }
    }

    /**
     * 刪除公告（需要管理員權限）
     */
    const deleteAnnouncement = async (id: string) => {
        try {
            await apiFetch(`/api/v1/announcements/${id}`, {
                method: 'DELETE',
            })
            return true
        } catch (error) {
            console.error('Failed to delete announcement:', error)
            throw error
        }
    }

    return {
        getAnnouncements,
        getAnnouncement,
        createAnnouncement,
        updateAnnouncement,
        deleteAnnouncement,
    }
}
