import type {
    Institution,
    InstitutionCreate,
    PaginatedResponse,
} from '@/types/models';
import { apiClient } from './client';

export const institutionsAPI = {
    list: async (): Promise<Institution[]> => {
        const response = await apiClient.get<PaginatedResponse<Institution>>('/institutions/');
        return response.results;
    },

    get: async (id: number): Promise<Institution> => {
        return apiClient.get<Institution>(`/institutions/${id}/`);
    },

    create: async (data: InstitutionCreate): Promise<Institution> => {
        return apiClient.post<Institution>('/institutions/', data);
    },

    update: async (id: number, data: Partial<InstitutionCreate>): Promise<Institution> => {
        return apiClient.patch<Institution>(`/institutions/${id}/`, data);
    },

    delete: async (id: number): Promise<void> => {
        return apiClient.delete<void>(`/institutions/${id}/`);
    },
};
