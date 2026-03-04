import type {
    Category,
    CategoryCreate,
    PaginatedResponse,
} from '@/types/models';
import { apiClient } from './client';

export const categoriesAPI = {
    list: async (): Promise<Category[]> => {
        const response = await apiClient.get<PaginatedResponse<Category>>('/categories/');
        return response.results;
    },

    get: async (id: number): Promise<Category> => {
        return apiClient.get<Category>(`/categories/${id}/`);
    },

    create: async (data: CategoryCreate): Promise<Category> => {
        return apiClient.post<Category>('/categories/', data);
    },

    update: async (id: number, data: Partial<CategoryCreate>): Promise<Category> => {
        return apiClient.patch<Category>(`/categories/${id}/`, data);
    },

    delete: async (id: number): Promise<void> => {
        return apiClient.delete<void>(`/categories/${id}/`);
    },
};
