import type {
    Account,
    AccountCreate,
    PaginatedResponse,
} from '@/types/models';
import { apiClient } from './client';

export const accountsAPI = {
    list: async (): Promise<Account[]> => {
        const response = await apiClient.get<PaginatedResponse<Account>>('/accounts/');
        return response.results;
    },

    get: async (id: number): Promise<Account> => {
        return apiClient.get<Account>(`/accounts/${id}/`);
    },

    create: async (data: AccountCreate): Promise<Account> => {
        return apiClient.post<Account>('/accounts/', data);
    },

    update: async (id: number, data: Partial<AccountCreate>): Promise<Account> => {
        return apiClient.patch<Account>(`/accounts/${id}/`, data);
    },

    delete: async (id: number): Promise<void> => {
        return apiClient.delete<void>(`/accounts/${id}/`);
    },
};
